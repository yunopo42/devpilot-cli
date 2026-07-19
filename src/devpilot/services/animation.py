"""Terminal-independent animation policy and frame generation."""

import random
import string
from collections.abc import Mapping
from dataclasses import dataclass

from ..models.config import AppConfig

BOOT_STEPS = (
    "[BOOT] Initializing DevPilot Core...",
    "[BOOT] Loading command modules...",
    "[BOOT] Verifying configuration...",
    "[BOOT] Preparing terminal interface...",
    "[OK]   System ready.",
)
MATRIX_CHARACTERS = string.ascii_letters + string.digits + "01@#$%&"
CI_ENVIRONMENT_KEYS = (
    "CI",
    "GITHUB_ACTIONS",
    "GITLAB_CI",
    "TF_BUILD",
    "BUILDKITE",
)


@dataclass(frozen=True, slots=True)
class AnimationPolicy:
    """Decision describing whether animation is safe for one invocation."""

    enabled: bool
    reason: str | None = None


def resolve_animation_policy(
    config: AppConfig,
    *,
    no_animation: bool,
    is_terminal: bool,
    environment: Mapping[str, str],
) -> AnimationPolicy:
    """Resolve CLI, accessibility, CI, and terminal animation constraints."""
    if no_animation:
        return AnimationPolicy(False, "disabled by --no-animation")
    if config.reduced_motion:
        return AnimationPolicy(False, "disabled by reduced-motion")
    if not config.animations:
        return AnimationPolicy(False, "disabled in configuration")
    if any(environment.get(key) for key in CI_ENVIRONMENT_KEYS):
        return AnimationPolicy(False, "disabled in CI")
    if not is_terminal:
        return AnimationPolicy(False, "output is not an interactive terminal")
    return AnimationPolicy(True)


def generate_matrix_frame(
    width: int,
    height: int,
    *,
    random_source: random.Random,
) -> str:
    """Generate one bounded Matrix-style terminal frame."""
    safe_width = max(1, min(width, 240))
    safe_height = max(1, min(height, 100))
    lines: list[str] = []

    for _ in range(safe_height):
        line = "".join(
            random_source.choice(MATRIX_CHARACTERS)
            if random_source.random() < 0.16
            else " "
            for _ in range(safe_width)
        )
        lines.append(line.rstrip())

    return "\n".join(lines)
