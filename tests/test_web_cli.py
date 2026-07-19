"""Tests for the DevPilot web command group."""

from typer.testing import CliRunner

import devpilot.commands.web as web_commands
from devpilot.cli import app
from devpilot.models.web import FetchResult, PageLink, RobotsResult

runner = CliRunner()


class DummyClient:
    """No-network context manager used by CLI presentation tests."""

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None


def sample_page() -> FetchResult:
    """Return stable HTML response data."""
    return FetchResult(
        url="https://example.com/",
        status_code=200,
        content_type="text/html",
        content="<title>Example Domain</title><a href='/docs'>Docs</a>",
        size_bytes=61,
    )


def test_web_fetch_command(monkeypatch) -> None:
    """Fetch should display response metadata and bounded content."""
    monkeypatch.setattr(web_commands, "SafeHttpClient", DummyClient)
    monkeypatch.setattr(web_commands, "fetch_page", lambda *_args: sample_page())

    result = runner.invoke(app, ["web", "fetch", "https://example.com"])

    assert result.exit_code == 0
    assert "Web Response" in result.stdout
    assert "Example Domain" in result.stdout


def test_web_title_command(monkeypatch) -> None:
    """Title should display the normalized page title."""
    monkeypatch.setattr(web_commands, "SafeHttpClient", DummyClient)
    monkeypatch.setattr(
        web_commands, "fetch_page", lambda *_args, **_kwargs: sample_page()
    )

    result = runner.invoke(app, ["web", "title", "https://example.com"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "Example Domain"


def test_web_links_command(monkeypatch) -> None:
    """Links should be shown in a bounded table."""
    monkeypatch.setattr(web_commands, "SafeHttpClient", DummyClient)
    monkeypatch.setattr(
        web_commands, "fetch_page", lambda *_args, **_kwargs: sample_page()
    )
    monkeypatch.setattr(
        web_commands,
        "extract_links",
        lambda _page: (PageLink("https://example.com/docs", "Docs"),),
    )

    result = runner.invoke(app, ["web", "links", "https://example.com"])

    assert result.exit_code == 0
    assert "Page Links" in result.stdout
    assert "https://example.com/docs" in result.stdout


def test_web_robots_command(monkeypatch) -> None:
    """Robots should display the decision and source URL."""
    monkeypatch.setattr(web_commands, "SafeHttpClient", DummyClient)
    monkeypatch.setattr(
        web_commands,
        "check_robots",
        lambda *_args: RobotsResult(
            url="https://example.com/page",
            robots_url="https://example.com/robots.txt",
            allowed=True,
            status_code=200,
        ),
    )

    result = runner.invoke(app, ["web", "robots", "https://example.com/page"])

    assert result.exit_code == 0
    assert "robots.txt Check" in result.stdout
    assert "allowed" in result.stdout
