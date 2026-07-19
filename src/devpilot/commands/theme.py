"""Configuration and visual-theme commands."""

import os
import random
import time
from enum import StrEnum

import typer
from rich.live import Live
from rich.table import Table
from rich.text import Text

from ..core.console import console
from ..core.state import get_app_state
from ..core.theme import THEMES, palette_for
from ..models.config import AppConfig, ThemeName
from ..services.animation import (
    BOOT_STEPS,
    AnimationPolicy,
    generate_matrix_frame,
    resolve_animation_policy,
)
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


def current_animation_policy(ctx: typer.Context) -> AnimationPolicy:
    """Resolve animation policy for the current CLI invocation."""
    state = get_app_state(ctx.find_root().obj)
    return resolve_animation_policy(
        load_config(),
        no_animation=state.no_animation,
        is_terminal=console.is_terminal,
        environment=os.environ,
    )


def render_animation_fallback(policy: AnimationPolicy) -> None:
    """Explain why a visual effect was rendered statically."""
    palette = palette_for(ThemeName.HACKER)
    reason = policy.reason or "animation unavailable"
    console.print(f"Animation skipped: {reason}.", style=palette.muted)


def typewriter_line(text: str, *, delay: float = 0.012) -> None:
    """Print a single line character-by-character."""
    for character in text:
        console.print(character, end="", markup=False, soft_wrap=True)
        time.sleep(delay)
    console.print()


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


@hacker_app.command("boot")
def hacker_boot_command(ctx: typer.Context) -> None:
    """Display a bounded boot sequence with an accessible static fallback."""
    palette = palette_for(ThemeName.HACKER)
    policy = current_animation_policy(ctx)
    console.print(HACKER_BANNER, style=palette.primary, markup=False)

    if not policy.enabled:
        for step in BOOT_STEPS:
            console.print(step, style=palette.primary, markup=False)
        render_animation_fallback(policy)
        return

    for step in BOOT_STEPS:
        typewriter_line(step)
        time.sleep(0.08)


@hacker_app.command("matrix")
def hacker_matrix_command(
    ctx: typer.Context,
    duration: float = typer.Option(
        5.0,
        "--duration",
        "-d",
        min=1.0,
        max=15.0,
        help="Animation duration in seconds.",
    ),
) -> None:
    """Run a time-bounded Matrix-style terminal animation."""
    palette = palette_for(ThemeName.HACKER)
    policy = current_animation_policy(ctx)
    if not policy.enabled:
        console.print(HACKER_BANNER, style=palette.primary, markup=False)
        render_animation_fallback(policy)
        return

    random_source = random.Random()
    deadline = time.monotonic() + duration
    try:
        with Live(
            Text("", style=palette.primary),
            console=console,
            refresh_per_second=12,
            transient=True,
        ) as live:
            while time.monotonic() < deadline:
                size = console.size
                frame = generate_matrix_frame(
                    size.width,
                    max(1, size.height - 2),
                    random_source=random_source,
                )
                live.update(Text(frame, style=palette.primary))
                time.sleep(0.08)
    except KeyboardInterrupt:
        console.print("Matrix interrupted.", style=palette.muted)
        return

    console.print("Matrix sequence complete.", style=palette.success)
