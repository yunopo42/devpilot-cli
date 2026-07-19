"""Tests for JSON validation, formatting, and atomic writes."""

from pathlib import Path

import pytest

from devpilot.services.json_tools import (
    JsonToolError,
    format_json,
    parse_json,
    read_text_file,
    write_text_atomic,
)


def test_format_json_preserves_unicode_and_adds_newline() -> None:
    """Formatted JSON should be readable UTF-8 with a final newline."""
    formatted = format_json('{"message":"Merhaba dünya","count":2}')

    assert formatted == ('{\n  "message": "Merhaba dünya",\n  "count": 2\n}\n')


def test_parse_json_reports_line_and_column() -> None:
    """Invalid JSON errors should identify the failing location."""
    with pytest.raises(JsonToolError, match=r"line 1, column 8"):
        parse_json('{"key":}')


def test_read_text_file_rejects_missing_file(tmp_path: Path) -> None:
    """Missing JSON files should produce an application error."""
    with pytest.raises(JsonToolError, match="File does not exist"):
        read_text_file(tmp_path / "missing.json")


def test_write_text_atomic_replaces_file_without_temp_artifacts(
    tmp_path: Path,
) -> None:
    """Atomic writes should replace content and clean temporary files."""
    source = tmp_path / "data.json"
    source.write_text('{"value":1}', encoding="utf-8")

    write_text_atomic(source, '{\n  "value": 1\n}\n')

    assert source.read_text(encoding="utf-8") == '{\n  "value": 1\n}\n'
    assert list(tmp_path.glob(".data.json.*.tmp")) == []
