"""Built-in visual theme palettes."""

from dataclasses import dataclass

from ..models.config import ThemeName


@dataclass(frozen=True, slots=True)
class ThemePalette:
    """Semantic Rich styles used by command renderers."""

    primary: str
    accent: str
    success: str
    warning: str
    error: str
    muted: str


THEMES = {
    ThemeName.STANDARD: ThemePalette(
        primary="cyan",
        accent="bold blue",
        success="green",
        warning="yellow",
        error="bold red",
        muted="dim",
    ),
    ThemeName.HACKER: ThemePalette(
        primary="bright_green",
        accent="bold bright_green",
        success="bold green",
        warning="bright_yellow",
        error="bold bright_red",
        muted="green dim",
    ),
}


def palette_for(theme: ThemeName) -> ThemePalette:
    """Return the immutable palette for a built-in theme."""
    return THEMES[theme]


def active_palette() -> ThemePalette:
    """Load and return the currently configured palette."""
    from ..services.config import load_config

    return palette_for(load_config().theme)
