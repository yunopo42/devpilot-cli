"""Runtime state shared between DevPilot commands."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppState:
    """Options that apply to the complete CLI invocation."""

    debug: bool = False
