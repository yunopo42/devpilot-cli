"""Runtime state shared between DevPilot commands."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppState:
    """Options that apply to the complete CLI invocation."""

    debug: bool = False
    no_animation: bool = False


def get_app_state(context_object: object) -> AppState:
    """Return validated CLI state or safe defaults."""
    if isinstance(context_object, AppState):
        return context_object
    return AppState()
