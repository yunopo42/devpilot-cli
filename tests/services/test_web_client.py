"""Tests for bounded public-network HTTP requests."""

import socket

import httpx
import pytest

from devpilot.services.web_client import (
    MAX_RESPONSE_BYTES,
    USER_AGENT,
    SafeHttpClient,
    WebRequestError,
    validate_connected_peer,
    validate_public_url,
)

PUBLIC_IP = "93.184.216.34"


def public_resolver(hostname: str, *_args, **_kwargs) -> list[tuple]:
    """Resolve test hostnames to a documentation public address."""
    return [
        (
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP,
            "",
            (PUBLIC_IP, 0),
        )
    ]


@pytest.mark.parametrize(
    "url",
    [
        "ftp://example.com/file",
        "https://user:secret@example.com/",
        "http://127.0.0.1/",
        "http://10.0.0.1/",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]/",
    ],
)
def test_validate_public_url_rejects_unsafe_targets(url: str) -> None:
    """Credentials, unsupported schemes, and non-public IPs must be blocked."""
    with pytest.raises(WebRequestError):
        validate_public_url(url, resolver=public_resolver)


def test_validate_public_url_accepts_public_dns_target() -> None:
    """A credential-free HTTPS URL resolving publicly should be accepted."""
    result = validate_public_url(
        "https://example.com/path",
        resolver=public_resolver,
    )

    assert result.addresses == (PUBLIC_IP,)


def test_validate_connected_peer_rejects_private_transport_address() -> None:
    """The actual peer should be checked after DNS validation."""

    class PrivateNetworkStream:
        def get_extra_info(self, name: str):
            assert name == "server_addr"
            return ("127.0.0.1", 443)

    response = httpx.Response(
        200,
        extensions={"network_stream": PrivateNetworkStream()},
    )

    with pytest.raises(WebRequestError, match="reached a non-public"):
        validate_connected_peer(response)


def test_fetch_sends_user_agent_and_returns_text() -> None:
    """Safe requests should identify DevPilot and return bounded text metadata."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["user-agent"] == USER_AGENT
        return httpx.Response(
            200,
            headers={"content-type": "text/plain; charset=utf-8"},
            text="hello",
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = SafeHttpClient(client=http_client, resolver=public_resolver)

    result = client.fetch("https://example.com/data")

    assert result.status_code == 200
    assert result.content_type == "text/plain"
    assert result.content == "hello"
    assert result.size_bytes == 5
    http_client.close()


def test_fetch_revalidates_redirect_destination() -> None:
    """A public page must not redirect into a private network."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "http://127.0.0.1/admin"})

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = SafeHttpClient(client=http_client, resolver=public_resolver)

    with pytest.raises(WebRequestError, match="non-public"):
        client.fetch("https://example.com/start")

    http_client.close()


def test_fetch_enforces_redirect_limit() -> None:
    """Redirect chains should stop after the configured maximum."""
    request_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal request_count
        request_count += 1
        return httpx.Response(302, headers={"location": f"/next-{request_count}"})

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = SafeHttpClient(client=http_client, resolver=public_resolver)

    with pytest.raises(WebRequestError, match="Maximum redirect"):
        client.fetch("https://example.com/start")

    assert request_count == 4
    http_client.close()


def test_fetch_converts_http_timeout_to_application_error() -> None:
    """Transport timeouts should become clean DevPilot errors."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = SafeHttpClient(client=http_client, resolver=public_resolver)

    with pytest.raises(WebRequestError, match="HTTP request failed"):
        client.fetch("https://example.com/slow")

    http_client.close()


def test_fetch_rejects_declared_oversized_response() -> None:
    """Content-Length should be checked before reading the body."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={
                "content-type": "text/plain",
                "content-length": str(MAX_RESPONSE_BYTES + 1),
            },
            content=b"small",
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = SafeHttpClient(client=http_client, resolver=public_resolver)

    with pytest.raises(WebRequestError, match="2 MiB"):
        client.fetch("https://example.com/large")

    http_client.close()


def test_fetch_rejects_streamed_oversized_response() -> None:
    """Actual decoded body size should be enforced without Content-Length."""
    body = b"x" * (MAX_RESPONSE_BYTES + 1)

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/plain"},
            content=body,
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = SafeHttpClient(client=http_client, resolver=public_resolver)

    with pytest.raises(WebRequestError, match="2 MiB"):
        client.fetch("https://example.com/stream")

    http_client.close()


def test_fetch_rejects_non_text_content() -> None:
    """Binary downloads should remain outside the MVP web client."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/octet-stream"},
            content=b"binary",
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = SafeHttpClient(client=http_client, resolver=public_resolver)

    with pytest.raises(WebRequestError, match="Only text"):
        client.fetch("https://example.com/file")

    http_client.close()
