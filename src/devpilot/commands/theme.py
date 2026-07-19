"""Configuration and visual-theme commands."""

from enum import StrEnum

import typer
from rich.table import Table

from ..core.console import console
from ..core.theme import THEMES, palette_for
from ..models.config import AppConfig, ThemeName
from ..services.config import (
    get_config_path,
    load_config,
    reset_config,
    set_boolean_setting,
    set_theme,
)

HACKER_BANNER = r"""
 ____             ____  _ _       _
|  _ \  _____   _|  _ \(_) | ___ | |_
| | | |/ _ \ \ / / |_) | | |/ _ \| __|
| |_| |  __/\ V /|  __/| | | (_) | |_
|____/ \___| \_/ |_|   |_|_|\___/ \__|

        DevPilot CLI // DEVELOPER ACCESS CONSOLE
""".strip("\n")


class ConfigKey(StrEnum):
    """Boolean settings editable from the CLI."""

    ANIMATIONS = "animations"
    REDUCED_MOTION = "reduced-motion"


class BooleanValue(StrEnum):
    """Explicit boolean values accepted by config commands."""

    TRUE = "true"
    FALSE = "false"


config_app = typer.Typer(
    help="Inspect and update persistent DevPilot settings.",
    no_args_is_help=True,
)
theme_app = typer.Typer(
    help="List and select built-in visual themes.",
    no_args_is_help=True,
)
hacker_app = typer.Typer(
    help="Display optional hacker-style visual elements.",
    no_args_is_help=True,
)


def render_config(config: AppConfig) -> None:
    """Render validated settings and their storage location."""
    palette = palette_for(config.theme)
    table = Table(title="DevPilot Configuration")
    table.add_column("Setting", style=palette.primary)
    table.add_column("Value")
    table.add_row("theme", config.theme.value)
    table.add_row("animations", str(config.animations).lower())
    table.add_row("reduced-motion", str(config.reduced_motion).lower())
    table.add_row("effective animations", str(config.animations_enabled).lower())
    table.add_row("config path", str(get_config_path()))
    console.print(table)


@config_app.command("show")
def config_show_command() -> None:
    """Show effective settings and the config file location."""
    render_config(load_config())


@config_app.command("set")
def config_set_command(
    key: ConfigKey = typer.Argument(..., help="Setting to update."),
    value: BooleanValue = typer.Argument(..., help="Boolean value."),
) -> None:
    """Set an animation-related boolean setting."""
    field_name = key.value.replace("-", "_")
    updated = set_boolean_setting(field_name, value is BooleanValue.TRUE)
    palette = palette_for(updated.theme)
    console.print(
        f"[{palette.success}]Updated:[/{palette.success}] {key.value}={value.value}"
    )


@config_app.command("reset")
def config_reset_command() -> None:
    """Restore validated default settings."""
    updated = reset_config()
    palette = palette_for(updated.theme)
    console.print(f"[{palette.success}]Configuration reset.[/{palette.success}]")


@theme_app.command("list")
def theme_list_command() -> None:
    """List built-in themes and mark the active one."""
    active = load_config().theme
    palette = palette_for(active)
    table = Table(title="DevPilot Themes")
    table.add_column("Theme", style=palette.primary)
    table.add_column("Active")
    table.add_column("Description")
    descriptions = {
        ThemeName.STANDARD: "Clean cyan and blue terminal output",
        ThemeName.HACKER: "Green high-contrast developer aesthetic",
    }
    for theme in THEMES:
        selected = "yes" if theme is active else ""
        table.add_row(theme.value, selected, descriptions[theme])
    console.print(table)


@theme_app.command("set")
def theme_set_command(
    theme: ThemeName = typer.Argument(..., help="Theme to activate."),
) -> None:
    """Persist the selected visual theme."""
    updated = set_theme(theme)
    palette = palette_for(updated.theme)
    console.print(
        f"[{palette.success}]Theme set:[/{palette.success}] {updated.theme.value}"
    )


@hacker_app.command("banner")
def hacker_banner_command() -> None:
    """Display the static Hacker Mode banner without animation."""
    palette = palette_for(ThemeName.HACKER)
    console.print(HACKER_BANNER, style=palette.primary, markup=False)
