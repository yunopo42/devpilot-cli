"""Persistent, validated DevPilot configuration."""

import os
import tempfile
from pathlib import Path

from platformdirs import user_config_path
from pydantic import ValidationError

from ..core.errors import DevPilotError
from ..models.config import AppConfig, ThemeName

CONFIG_DIRECTORY_ENV = "DEVPILOT_CONFIG_DIR"


class ConfigError(DevPilotError):
    """Raised when configuration cannot be loaded or saved safely."""


def get_config_path() -> Path:
    """Return the platform-appropriate DevPilot configuration file."""
    override = os.environ.get(CONFIG_DIRECTORY_ENV)
    if override:
        return Path(override).expanduser() / "config.json"
    return user_config_path("DevPilot", appauthor=False) / "config.json"


def load_config(path: Path | None = None) -> AppConfig:
    """Load validated configuration, returning defaults when absent."""
    config_path = path or get_config_path()
    if not config_path.exists():
        return AppConfig()

    try:
        content = config_path.read_text(encoding="utf-8")
        return AppConfig.model_validate_json(content)
    except UnicodeDecodeError as error:
        raise ConfigError(f"Config is not valid UTF-8: {config_path}") from error
    except ValidationError as error:
        detail = error.errors(include_url=False)[0]["msg"]
        message = f"Config is invalid: {detail}. Path: {config_path}"
        raise ConfigError(message) from error
    except OSError as error:
        raise ConfigError(f"Config could not be read: {config_path}") from error


def save_config(config: AppConfig, path: Path | None = None) -> Path:
    """Persist configuration using an atomic file replacement."""
    config_path = path or get_config_path()
    temporary_path: Path | None = None
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=config_path.parent,
            prefix=".config.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_file.write(config.model_dump_json(indent=2) + "\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
            temporary_path = Path(temporary_file.name)

        os.replace(temporary_path, config_path)
        return config_path
    except OSError as error:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise ConfigError(f"Config could not be saved: {config_path}") from error


def set_theme(theme: ThemeName, path: Path | None = None) -> AppConfig:
    """Update only the active theme and preserve other settings."""
    config = load_config(path)
    updated = config.model_copy(update={"theme": theme})
    save_config(updated, path)
    return updated


def set_boolean_setting(
    name: str,
    value: bool,
    path: Path | None = None,
) -> AppConfig:
    """Update one supported boolean setting."""
    if name not in {"animations", "reduced_motion"}:
        raise ConfigError(f"Unsupported boolean setting: {name}")
    config = load_config(path)
    updated = config.model_copy(update={name: value})
    save_config(updated, path)
    return updated


def reset_config(path: Path | None = None) -> AppConfig:
    """Replace configuration with validated defaults."""
    config = AppConfig()
    save_config(config, path)
    return config
