"""Command-line interface for DevPilot."""

import typer

app = typer.Typer(
    name="devpilot",
    help="A modular developer toolkit for the terminal.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Run the DevPilot command-line application."""
