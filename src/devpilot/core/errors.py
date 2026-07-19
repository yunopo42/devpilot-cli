"""Application-specific errors and their terminal presentation."""

from .console import error_console


class DevPilotError(Exception):
    """Base class for errors that can be shown safely to users."""


def render_error(error: DevPilotError, *, debug: bool = False) -> None:
    """Display a known application error with optional debug details."""
    if debug:
        error_console.print_exception(show_locals=False)
        return

    error_console.print(f"[bold red]Error:[/bold red] {error}")
