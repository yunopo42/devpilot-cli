"""Tests for the top-level DevPilot error boundary."""

import pytest

import devpilot.cli as cli
from devpilot.core.errors import DevPilotError


def test_run_converts_known_error_to_exit_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Known errors should become a clean non-zero process exit."""
    rendered_errors: list[tuple[str, bool]] = []

    def failing_app() -> None:
        raise DevPilotError("expected failure")

    def capture_error(error: DevPilotError, *, debug: bool = False) -> None:
        rendered_errors.append((str(error), debug))

    monkeypatch.setattr(cli, "app", failing_app)
    monkeypatch.setattr(cli, "render_error", capture_error)

    with pytest.raises(SystemExit) as exit_info:
        cli.run()

    assert exit_info.value.code == 1
    assert rendered_errors == [("expected failure", False)]
