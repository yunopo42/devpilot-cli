"""JSON validation, formatting, and safe file writing."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from ..core.errors import DevPilotError


class JsonToolError(DevPilotError):
    """Raised when JSON input cannot be processed safely."""


def parse_json(text: str) -> Any:
    """Parse JSON text and provide a readable location on failure."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise JsonToolError(
            f"Invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}."
        ) from error


def format_json(text: str, *, indent: int = 2, sort_keys: bool = False) -> str:
    """Return normalized, UTF-8-friendly JSON text with a trailing newline."""
    data = parse_json(text)
    return (
        json.dumps(
            data,
            ensure_ascii=False,
            indent=indent,
            sort_keys=sort_keys,
        )
        + "\n"
    )


def read_text_file(path: Path) -> str:
    """Read a UTF-8 text file with application-level errors."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise JsonToolError(f"File does not exist: {path}") from error
    except UnicodeDecodeError as error:
        raise JsonToolError(f"File is not valid UTF-8 text: {path}") from error
    except OSError as error:
        raise JsonToolError(f"File could not be read: {path}") from error


def write_text_atomic(path: Path, content: str) -> None:
    """Replace a file atomically after writing a complete temporary copy."""
    try:
        original_mode = path.stat().st_mode
    except FileNotFoundError as error:
        raise JsonToolError(f"File does not exist: {path}") from error
    except OSError as error:
        raise JsonToolError(f"File metadata could not be read: {path}") from error

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
            temporary_path = Path(temporary_file.name)

        os.chmod(temporary_path, original_mode)
        os.replace(temporary_path, path)
    except OSError as error:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise JsonToolError(f"File could not be updated safely: {path}") from error
