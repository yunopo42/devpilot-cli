"""Structured results returned by web services."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FetchResult:
    """Bounded text response fetched from a public URL."""

    url: str
    status_code: int
    content_type: str
    content: str
    size_bytes: int


@dataclass(frozen=True, slots=True)
class PageLink:
    """One normalized HTTP link extracted from an HTML page."""

    url: str
    text: str


@dataclass(frozen=True, slots=True)
class RobotsResult:
    """robots.txt decision for a URL and the DevPilot user agent."""

    url: str
    robots_url: str
    allowed: bool
    status_code: int
