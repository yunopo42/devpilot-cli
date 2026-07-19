"""Tests for DevPilot configuration and theme commands."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from devpilot.cli import app
from devpilot.core.theme import palette_for
from devpilot.models.config import ThemeName
from devpilot.services.config import CONFIG_DIRECTORY_ENV, load_config

runner = CliRunner()


@pytest.fixture
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect configuration commands to a temporary directory."""
    monkeypatch.setenv(CONFIG_DIRECTORY_ENV, str(tmp_path))
    return tmp_path / "config.json"


def test_config_show_uses_defaults_without_creating_file(
    isolated_config: Path,
) -> None:
    """Showing first-run defaults should not write to disk."""
    result = runner.invoke(app, ["config", "show"])

    assert result.exit_code == 0
    assert "DevPilot Configuration" in result.stdout
    assert "standard" in result.stdout
    assert not isolated_config.exists()


def test_config_set_updates_reduced_motion(isolated_config: Path) -> None:
    """Boolean settings should persist explicit CLI values."""
    result = runner.invoke(
        app,
        ["config", "set", "reduced-motion", "true"],
    )

    assert result.exit_code == 0
    assert load_config(isolated_config).reduced_motion is True
    assert load_config(isolated_config).animations_enabled is False


def test_theme_set_and_list_persist_selection(isolated_config: Path) -> None:
    """Theme selection should persist and appear in the theme list."""
    selected = runner.invoke(app, ["theme", "set", "hacker"])
    listed = runner.invoke(app, ["theme", "list"])

    assert selected.exit_code == 0
    assert listed.exit_code == 0
    assert load_config(isolated_config).theme is ThemeName.HACKER
    assert "hacker" in listed.stdout
    assert "yes" in listed.stdout


def test_config_reset_recovers_invalid_file(isolated_config: Path) -> None:
    """Users should be able to recover from manually corrupted config."""
    isolated_config.write_text("not-json", encoding="utf-8")

    result = runner.invoke(app, ["config", "reset"])

    assert result.exit_code == 0
    assert load_config(isolated_config).theme is ThemeName.STANDARD


def test_hacker_banner_is_static_and_available(isolated_config: Path) -> None:
    """The Hacker banner should render without requiring animations."""
    result = runner.invoke(app, ["hacker", "banner"])

    assert result.exit_code == 0
    assert "DevPilot" in result.stdout
    assert "DEVELOPER ACCESS CONSOLE" in result.stdout
    assert not isolated_config.exists()


def test_hacker_palette_differs_from_standard() -> None:
    """Built-in themes should map semantic roles to distinct styles."""
    standard = palette_for(ThemeName.STANDARD)
    hacker = palette_for(ThemeName.HACKER)

    assert standard.primary != hacker.primary
    assert standard.accent != hacker.accent
