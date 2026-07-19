"""Tests for animation policy and frame generation."""

import random

import pytest

from devpilot.models.config import AppConfig
from devpilot.services.animation import (
    generate_matrix_frame,
    resolve_animation_policy,
)


@pytest.mark.parametrize(
    ("config", "no_animation", "is_terminal", "environment", "reason"),
    [
        (
            AppConfig(),
            True,
            True,
            {},
            "disabled by --no-animation",
        ),
        (
            AppConfig(reduced_motion=True),
            False,
            True,
            {},
            "disabled by reduced-motion",
        ),
        (
            AppConfig(animations=False),
            False,
            True,
            {},
            "disabled in configuration",
        ),
        (
            AppConfig(),
            False,
            True,
            {"CI": "true"},
            "disabled in CI",
        ),
        (
            AppConfig(),
            False,
            False,
            {},
            "output is not an interactive terminal",
        ),
    ],
)
def test_animation_policy_disables_unsafe_or_unwanted_motion(
    config: AppConfig,
    no_animation: bool,
    is_terminal: bool,
    environment: dict[str, str],
    reason: str,
) -> None:
    """Every opt-out and non-interactive condition should have a reason."""
    policy = resolve_animation_policy(
        config,
        no_animation=no_animation,
        is_terminal=is_terminal,
        environment=environment,
    )

    assert policy.enabled is False
    assert policy.reason == reason


def test_animation_policy_enables_interactive_motion() -> None:
    """Animation should run only when all constraints allow it."""
    policy = resolve_animation_policy(
        AppConfig(),
        no_animation=False,
        is_terminal=True,
        environment={},
    )

    assert policy.enabled is True
    assert policy.reason is None


def test_matrix_frame_is_deterministic_and_bounded() -> None:
    """Injected randomness should make frame generation testable and bounded."""
    first = generate_matrix_frame(
        12,
        4,
        random_source=random.Random(42),
    )
    second = generate_matrix_frame(
        12,
        4,
        random_source=random.Random(42),
    )

    assert first == second
    assert len(first.splitlines()) <= 4
    assert all(len(line) <= 12 for line in first.splitlines())


def test_matrix_frame_caps_extreme_terminal_sizes() -> None:
    """Frame generation should cap work for unexpectedly large terminals."""
    frame = generate_matrix_frame(
        10_000,
        10_000,
        random_source=random.Random(1),
    )

    lines = frame.splitlines()
    assert len(lines) <= 100
    assert all(len(line) <= 240 for line in lines)
