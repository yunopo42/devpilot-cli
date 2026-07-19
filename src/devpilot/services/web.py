"""robots.txt-aware page retrieval and HTML extraction."""

from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup

from ..core.errors import DevPilotError
from ..models.web import FetchResult, PageLink, RobotsResult
from .web_client import USER_AGENT, SafeHttpClient


class WebContentError(DevPilotError):
    """Raised when web content cannot be safely interpreted."""


class RobotsDeniedError(DevPilotError):
    """Raised when robots.txt disallows a requested URL."""


def build_robots_url(url: str) -> str:
    """Return the origin-level robots.txt URL for a page URL."""
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme, parsed.netloc, "/robots.txt", "", ""))


def check_robots(client: SafeHttpClient, url: str) -> RobotsResult:
    """Check robots.txt for the DevPilot user agent."""
    client.validate_url(url)
    robots_url = build_robots_url(url)
    response = client.fetch(
        robots_url,
        accepted_statuses={401, 403, 404},
    )

    if response.status_code == 404:
        allowed = True
    elif response.status_code in {401, 403}:
        allowed = False
    else:
        parser = RobotFileParser()
        parser.set_url(robots_url)
        parser.parse(response.content.splitlines())
        allowed = parser.can_fetch(USER_AGENT, url)

    return RobotsResult(
        url=url,
        robots_url=robots_url,
        allowed=allowed,
        status_code=response.status_code,
    )


def fetch_page(
    client: SafeHttpClient,
    url: str,
    *,
    require_html: bool = False,
) -> FetchResult:
    """Fetch a page only when robots.txt allows DevPilot access."""
    robots = check_robots(client, url)
    if not robots.allowed:
        raise RobotsDeniedError(f"robots.txt does not allow access to: {url}")
    return client.fetch(url, require_html=require_html)


def extract_title(page: FetchResult) -> str:
    """Extract a normalized HTML title."""
    soup = BeautifulSoup(page.content, "html.parser")
    if soup.title is None:
        raise WebContentError("The HTML page does not contain a title.")
    title = " ".join(soup.title.get_text(" ", strip=True).split())
    if not title:
        raise WebContentError("The HTML page title is empty.")
    return title


def extract_links(page: FetchResult) -> tuple[PageLink, ...]:
    """Extract unique, absolute, credential-free HTTP links from HTML."""
    soup = BeautifulSoup(page.content, "html.parser")
    links: list[PageLink] = []
    seen: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href")
        if not isinstance(href, str):
            continue
        absolute = urljoin(page.url, href.strip())
        parsed = urlsplit(absolute)
        if parsed.scheme.lower() not in {"http", "https"}:
            continue
        if (
            not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
        ):
            continue
        normalized = urlunsplit(
            (parsed.scheme.lower(), parsed.netloc, parsed.path or "/", parsed.query, "")
        )
        if normalized in seen:
            continue
        seen.add(normalized)
        links.append(
            PageLink(
                url=normalized,
                text=" ".join(anchor.get_text(" ", strip=True).split()),
            )
        )

    return tuple(links)
