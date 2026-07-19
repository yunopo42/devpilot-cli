"""Tests for persistent, validated application configuration."""

from pathlib import Path

import pytest

from devpilot.models.config import AppConfig, ThemeName
from devpilot.services.config import (
    CONFIG_DIRECTORY_ENV,
    ConfigError,
    get_config_path,
    load_config,
    reset_config,
    save_config,
    set_boolean_setting,
    set_theme,
)


def test_load_config_returns_defaults_when_file_is_absent(tmp_path: Path) -> None:
    """A first run should work without creating a config file."""
    config = load_config(tmp_path / "config.json")

    assert config == AppConfig()
    assert config.animations_enabled is True


def test_save_and_load_config_round_trip(tmp_path: Path) -> None:
    """Saved settings should round-trip through Pydantic validation."""
    path = tmp_path / "nested" / "config.json"
    expected = AppConfig(
        theme=ThemeName.HACKER,
        animations=True,
        reduced_motion=True,
    )

    saved_path = save_config(expected, path)
    loaded = load_config(path)

    assert saved_path == path
    assert loaded == expected
    assert loaded.animations_enabled is False
    assert list(path.parent.glob(".config.*.tmp")) == []


def test_load_config_rejects_unknown_fields(tmp_path: Path) -> None:
    """Unexpected settings should not be silently accepted."""
    path = tmp_path / "config.json"
    path.write_text('{"theme":"standard","unknown":true}', encoding="utf-8")

    with pytest.raises(ConfigError, match="Config is invalid"):
        load_config(path)


def test_setting_updates_preserve_other_values(tmp_path: Path) -> None:
    """Each settings command should update only its own field."""
    path = tmp_path / "config.json"
    save_config(AppConfig(theme=ThemeName.HACKER), path)

    animation_update = set_boolean_setting("animations", False, path)
    theme_update = set_theme(ThemeName.STANDARD, path)

    assert animation_update.theme is ThemeName.HACKER
    assert animation_update.animations is False
    assert theme_update.theme is ThemeName.STANDARD
    assert theme_update.animations is False


def test_reset_config_recovers_from_invalid_content(tmp_path: Path) -> None:
    """Reset should overwrite invalid config without loading it first."""
    path = tmp_path / "config.json"
    path.write_text("not-json", encoding="utf-8")

    reset = reset_config(path)

    assert reset == AppConfig()
    assert load_config(path) == AppConfig()


def test_config_directory_can_be_overridden_for_isolation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The documented environment override should control config location."""
    monkeypatch.setenv(CONFIG_DIRECTORY_ENV, str(tmp_path))

    assert get_config_path() == tmp_path / "config.json"
