"""Validated application configuration models."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ThemeName(StrEnum):
    """Built-in visual themes."""

    STANDARD = "standard"
    HACKER = "hacker"


class AppConfig(BaseModel):
    """Persistent, user-controlled DevPilot settings."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    theme: ThemeName = ThemeName.STANDARD
    animations: bool = True
    reduced_motion: bool = False

    @property
    def animations_enabled(self) -> bool:
        """Return whether motion is effectively allowed."""
        return self.animations and not self.reduced_motion
