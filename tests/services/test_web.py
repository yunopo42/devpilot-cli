"""Tests for robots-aware HTML services."""

import httpx
import pytest

from devpilot.models.web import FetchResult
from devpilot.services.web import (
    RobotsDeniedError,
    check_robots,
    extract_links,
    extract_title,
    fetch_page,
)
from devpilot.services.web_client import SafeHttpClient
from tests.services.test_web_client import public_resolver


def make_client(handler) -> tuple[SafeHttpClient, httpx.Client]:
    """Create a safe client backed by deterministic mock responses."""
    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    return (
        SafeHttpClient(client=http_client, resolver=public_resolver),
        http_client,
    )


def test_check_robots_allows_rule_permitted_page() -> None:
    """robots.txt rules should be evaluated for the DevPilot user agent."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/robots.txt"
        return httpx.Response(
            200,
            headers={"content-type": "text/plain"},
            text="User-agent: *\nDisallow: /private\n",
        )

    client, http_client = make_client(handler)
    result = check_robots(client, "https://example.com/public")

    assert result.allowed is True
    assert result.status_code == 200
    http_client.close()


def test_fetch_page_stops_when_robots_denies() -> None:
    """A denied robots rule should prevent the page request entirely."""
    requested_paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested_paths.append(request.url.path)
        return httpx.Response(
            200,
            headers={"content-type": "text/plain"},
            text="User-agent: *\nDisallow: /private\n",
        )

    client, http_client = make_client(handler)

    with pytest.raises(RobotsDeniedError, match="does not allow"):
        fetch_page(client, "https://example.com/private/data")

    assert requested_paths == ["/robots.txt"]
    http_client.close()


def test_missing_robots_file_allows_page() -> None:
    """A 404 robots.txt response should allow public page access."""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(404, text="")
        return httpx.Response(
            200,
            headers={"content-type": "text/html"},
            text="<title>Allowed</title>",
        )

    client, http_client = make_client(handler)
    page = fetch_page(client, "https://example.com/page", require_html=True)

    assert extract_title(page) == "Allowed"
    http_client.close()


def test_extract_title_and_normalized_unique_links() -> None:
    """HTML extraction should normalize links and remove unsafe duplicates."""
    page = FetchResult(
        url="https://example.com/docs/page",
        status_code=200,
        content_type="text/html",
        size_bytes=100,
        content="""
        <html><head><title> DevPilot   Docs </title></head><body>
          <a href="/guide#intro">Guide</a>
          <a href="https://example.com/guide">Duplicate</a>
          <a href="mailto:test@example.com">Mail</a>
          <a href="https://user:secret@example.com/private">Secret</a>
        </body></html>
        """,
    )

    links = extract_links(page)

    assert extract_title(page) == "DevPilot Docs"
    assert [(link.text, link.url) for link in links] == [
        ("Guide", "https://example.com/guide"),
    ]
