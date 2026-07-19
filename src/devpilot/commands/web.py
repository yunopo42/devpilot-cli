"""Safe, robots-aware web commands."""

import typer
from rich.table import Table

from ..core.console import console
from ..core.formatting import format_bytes
from ..core.theme import active_palette
from ..models.web import FetchResult, PageLink, RobotsResult
from ..services.web import check_robots, extract_links, extract_title, fetch_page
from ..services.web_client import SafeHttpClient

web_app = typer.Typer(
    help="Fetch and inspect public web pages within strict safety limits.",
    no_args_is_help=True,
)


def render_response_summary(response: FetchResult) -> None:
    """Render bounded HTTP response metadata."""
    palette = active_palette()
    table = Table(title="Web Response")
    table.add_column("Property", style=palette.primary)
    table.add_column("Value")
    table.add_row("URL", response.url)
    table.add_row("Status", str(response.status_code))
    table.add_row("Content type", response.content_type)
    table.add_row("Size", format_bytes(response.size_bytes))
    console.print(table)


def render_links(links: tuple[PageLink, ...], limit: int) -> None:
    """Render a bounded set of normalized links."""
    palette = active_palette()
    table = Table(title="Page Links")
    table.add_column("#", justify="right", style=palette.primary)
    table.add_column("Text")
    table.add_column("URL", overflow="fold")
    for index, link in enumerate(links[:limit], start=1):
        table.add_row(str(index), link.text or "—", link.url)
    console.print(table)
    console.print(f"Showing {min(len(links), limit)} of {len(links)} links.")


def render_robots(result: RobotsResult) -> None:
    """Render a robots.txt decision."""
    palette = active_palette()
    table = Table(title="robots.txt Check")
    table.add_column("Property", style=palette.primary)
    table.add_column("Value")
    table.add_row("URL", result.url)
    table.add_row("robots.txt", result.robots_url)
    table.add_row("Status", str(result.status_code))
    decision_style = palette.success if result.allowed else palette.error
    decision = "allowed" if result.allowed else "denied"
    table.add_row("Decision", f"[{decision_style}]{decision}[/{decision_style}]")
    console.print(table)


@web_app.command("fetch")
def fetch_command(
    url: str = typer.Argument(..., help="Public HTTP or HTTPS URL."),
) -> None:
    """Fetch a robots-allowed text response within the 2 MiB limit."""
    with SafeHttpClient() as client:
        response = fetch_page(client, url)
    render_response_summary(response)
    console.print(response.content, markup=False, soft_wrap=True)


@web_app.command("title")
def title_command(
    url: str = typer.Argument(..., help="Public HTML page URL."),
) -> None:
    """Fetch an allowed HTML page and display its title."""
    with SafeHttpClient() as client:
        page = fetch_page(client, url, require_html=True)
    console.print(extract_title(page), markup=False, soft_wrap=True)


@web_app.command("links")
def links_command(
    url: str = typer.Argument(..., help="Public HTML page URL."),
    limit: int = typer.Option(
        50,
        "--limit",
        "-n",
        min=1,
        max=200,
        help="Maximum links to display.",
    ),
) -> None:
    """Fetch an allowed HTML page and list normalized HTTP links."""
    with SafeHttpClient() as client:
        page = fetch_page(client, url, require_html=True)
    render_links(extract_links(page), limit)


@web_app.command("robots")
def robots_command(
    url: str = typer.Argument(..., help="Public URL to check."),
) -> None:
    """Check whether robots.txt allows DevPilot to fetch a URL."""
    with SafeHttpClient() as client:
        result = check_robots(client, url)
    render_robots(result)
