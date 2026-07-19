"""Command-line interface for DevPilot."""

import typer

from .commands.core import about_command, doctor_command, version_command
from .commands.dev import dev_app
from .commands.file import file_app
from .commands.system import system_app
from .commands.theme import config_app, hacker_app, theme_app
from .core.errors import DevPilotError, render_error
from .core.state import AppState

_active_state = AppState()

app = typer.Typer(
    name="devpilot",
    help="A modular developer toolkit for the terminal.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)


@app.callback()
def main(
    ctx: typer.Context,
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Show detailed diagnostic information when an error occurs.",
    ),
    no_animation: bool = typer.Option(
        False,
        "--no-animation",
        help="Disable animation for this invocation.",
    ),
) -> None:
    """Run the DevPilot command-line application."""
    global _active_state
    _active_state = AppState(debug=debug, no_animation=no_animation)
    ctx.obj = _active_state


app.command("version")(version_command)
app.command("about")(about_command)
app.command("doctor")(doctor_command)
app.add_typer(system_app, name="system")
app.add_typer(file_app, name="file")
app.add_typer(dev_app, name="dev")
app.add_typer(config_app, name="config")
app.add_typer(theme_app, name="theme")
app.add_typer(hacker_app, name="hacker")


def run() -> None:
    """Run DevPilot and present known application errors consistently."""
    global _active_state
    _active_state = AppState()

    try:
        app()
    except DevPilotError as error:
        render_error(error, debug=_active_state.debug)
        raise SystemExit(1) from error
