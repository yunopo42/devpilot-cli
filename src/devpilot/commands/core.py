"""Core commands available at the root of the DevPilot CLI."""

from importlib.metadata import PackageNotFoundError, version

from rich.panel import Panel
from rich.table import Table

from ..core.console import console
from ..services.doctor import run_doctor_checks


def get_version() -> str:
    """Return the installed DevPilot package version."""
    try:
        return version("devpilot-cli")
    except PackageNotFoundError:
        return "unknown"


def version_command() -> None:
    """Show the installed DevPilot version."""
    console.print(f"DevPilot CLI {get_version()}")


def about_command() -> None:
    """Show a short description of the project."""
    console.print(
        Panel.fit(
            "A modular developer toolkit for the terminal.\n"
            "Built with Python, Typer, and Rich.",
            title="DevPilot CLI",
            border_style="cyan",
        )
    )


def doctor_command() -> None:
    """Check whether the local environment can run DevPilot."""
    table = Table(title="DevPilot Doctor")
    table.add_column("Check", style="cyan")
    table.add_column("Status")
    table.add_column("Details")

    for check in run_doctor_checks():
        status = "[green]PASS[/green]" if check.passed else "[red]FAIL[/red]"
        table.add_row(check.name, status, check.details)

    console.print(table)
