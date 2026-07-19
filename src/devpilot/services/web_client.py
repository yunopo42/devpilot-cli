"""Bounded HTTP client with public-network URL validation."""

import ipaddress
import socket
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit

import httpx

from ..core.errors import DevPilotError
from ..models.web import FetchResult

USER_AGENT = "DevPilotCLI/0.1"
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_REDIRECTS = 3
REQUEST_TIMEOUT_SECONDS = 15.0
ALLOWED_TEXT_CONTENT_TYPES = (
    "text/",
    "application/json",
    "application/xml",
    "application/xhtml+xml",
)
REDIRECT_STATUS_CODES = {301, 302, 303, 307, 308}

Resolver = Callable[..., list[tuple]]


class WebRequestError(DevPilotError):
    """Raised when a web request violates safety limits or fails."""


@dataclass(frozen=True, slots=True)
class ValidatedUrl:
    """Public HTTP URL and addresses observed during validation."""

    url: str
    addresses: tuple[str, ...]


def _resolved_addresses(hostname: str, resolver: Resolver) -> tuple[str, ...]:
    """Resolve all IP addresses for a hostname."""
    try:
        records = resolver(hostname, None, type=socket.SOCK_STREAM)
    except OSError as error:
        raise WebRequestError(f"Host could not be resolved: {hostname}") from error

    addresses = tuple(dict.fromkeys(record[4][0] for record in records))
    if not addresses:
        raise WebRequestError(f"Host did not resolve to an IP address: {hostname}")
    return addresses


def validate_public_url(
    url: str,
    *,
    resolver: Resolver = socket.getaddrinfo,
) -> ValidatedUrl:
    """Allow only credential-free HTTP URLs resolving to public IPs."""
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as error:
        raise WebRequestError(f"URL is invalid: {url}") from error

    if parsed.scheme.lower() not in {"http", "https"}:
        raise WebRequestError("Only http and https URLs are supported.")
    if not parsed.hostname:
        raise WebRequestError("URL must include a hostname.")
    if parsed.username is not None or parsed.password is not None:
        raise WebRequestError("URLs containing credentials are not supported.")
    if port is not None and not 1 <= port <= 65535:
        raise WebRequestError("URL port must be between 1 and 65535.")

    try:
        literal_address = ipaddress.ip_address(parsed.hostname)
        addresses = (str(literal_address),)
    except ValueError:
        addresses = _resolved_addresses(parsed.hostname, resolver)

    for address_text in addresses:
        try:
            address = ipaddress.ip_address(address_text)
        except ValueError as error:
            raise WebRequestError(
                f"Host resolved to an invalid IP address: {address_text}"
            ) from error
        if not address.is_global:
            raise WebRequestError(
                f"URL resolves to a non-public address: {address_text}"
            )

    return ValidatedUrl(url=url, addresses=addresses)


def validate_connected_peer(response: httpx.Response) -> None:
    """Reject a non-public peer address reported by the active transport."""
    network_stream = response.extensions.get("network_stream")
    if network_stream is None:
        return
    server_address = network_stream.get_extra_info("server_addr")
    if not server_address:
        return
    address_text = server_address[0]
    try:
        address = ipaddress.ip_address(address_text)
    except ValueError as error:
        raise WebRequestError(
            f"Connection reported an invalid peer address: {address_text}"
        ) from error
    if not address.is_global:
        raise WebRequestError(
            f"Connection reached a non-public address: {address_text}"
        )


class SafeHttpClient:
    """HTTP client enforcing URL, redirect, timeout, and body-size limits."""

    def __init__(
        self,
        *,
        client: httpx.Client | None = None,
        resolver: Resolver = socket.getaddrinfo,
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx.Client(
            timeout=REQUEST_TIMEOUT_SECONDS,
            follow_redirects=False,
            trust_env=False,
            headers={"User-Agent": USER_AGENT},
        )
        self._resolver = resolver

    def close(self) -> None:
        """Close the owned HTTP connection pool."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> "SafeHttpClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def validate_url(self, url: str) -> ValidatedUrl:
        """Validate a URL with this client's resolver."""
        return validate_public_url(url, resolver=self._resolver)

    def fetch(
        self,
        url: str,
        *,
        require_html: bool = False,
        accepted_statuses: Iterable[int] = (),
    ) -> FetchResult:
        """Fetch bounded text while validating every redirect destination."""
        current_url = url
        accepted = set(accepted_statuses)

        for redirect_count in range(MAX_REDIRECTS + 1):
            self.validate_url(current_url)
            try:
                with self._client.stream(
                    "GET",
                    current_url,
                    headers={"User-Agent": USER_AGENT},
                ) as response:
                    validate_connected_peer(response)
                    if response.status_code in REDIRECT_STATUS_CODES:
                        location = response.headers.get("location")
                        if not location:
                            raise WebRequestError("Redirect response has no location.")
                        if redirect_count >= MAX_REDIRECTS:
                            raise WebRequestError("Maximum redirect count exceeded.")
                        current_url = urljoin(str(response.url), location)
                        continue

                    if (
                        response.status_code >= 400
                        and response.status_code not in accepted
                    ):
                        raise WebRequestError(
                            f"HTTP request failed with status {response.status_code}."
                        )

                    content_type = response.headers.get("content-type", "")
                    normalized_type = content_type.split(";", 1)[0].strip().lower()
                    if response.status_code in accepted and not normalized_type:
                        normalized_type = "text/plain"
                    if require_html and normalized_type not in {
                        "text/html",
                        "application/xhtml+xml",
                    }:
                        raise WebRequestError("The response is not HTML content.")
                    if not any(
                        normalized_type.startswith(prefix)
                        for prefix in ALLOWED_TEXT_CONTENT_TYPES
                    ):
                        raise WebRequestError("Only text responses are supported.")

                    declared_length = response.headers.get("content-length")
                    if declared_length:
                        try:
                            too_large = int(declared_length) > MAX_RESPONSE_BYTES
                        except ValueError as error:
                            raise WebRequestError(
                                "Response has an invalid Content-Length header."
                            ) from error
                        if too_large:
                            raise WebRequestError(
                                "Response exceeds the 2 MiB size limit."
                            )

                    body = bytearray()
                    for chunk in response.iter_bytes():
                        body.extend(chunk)
                        if len(body) > MAX_RESPONSE_BYTES:
                            raise WebRequestError(
                                "Response exceeds the 2 MiB size limit."
                            )

                    encoding = response.encoding or "utf-8"
                    try:
                        content = bytes(body).decode(encoding, errors="replace")
                    except LookupError:
                        content = bytes(body).decode("utf-8", errors="replace")

                    return FetchResult(
                        url=str(response.url),
                        status_code=response.status_code,
                        content_type=normalized_type,
                        content=content,
                        size_bytes=len(body),
                    )
            except httpx.HTTPError as error:
                raise WebRequestError(f"HTTP request failed: {error}") from error

        raise WebRequestError("Maximum redirect count exceeded.")
