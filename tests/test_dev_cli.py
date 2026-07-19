"""Tests for the DevPilot developer command group."""

import json
from pathlib import Path

from typer.testing import CliRunner

from devpilot.cli import app

runner = CliRunner()


def test_json_format_from_file(tmp_path: Path) -> None:
    """JSON format should print normalized content without changing the file."""
    source = tmp_path / "data.json"
    original = '{"b":2,"a":1}'
    source.write_text(original, encoding="utf-8")

    result = runner.invoke(app, ["dev", "json", "format", str(source)])

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"b": 2, "a": 1}
    assert source.read_text(encoding="utf-8") == original


def test_json_format_from_stdin() -> None:
    """JSON format should read standard input when no file is given."""
    result = runner.invoke(
        app,
        ["dev", "json", "format", "--sort-keys"],
        input='{ "z": 1, "a": 2 }',
    )

    assert result.exit_code == 0
    assert result.stdout.index('"a"') < result.stdout.index('"z"')


def test_json_format_write_updates_file(tmp_path: Path) -> None:
    """The explicit write option should atomically update the source file."""
    source = tmp_path / "data.json"
    source.write_text('{"value":1}', encoding="utf-8")

    result = runner.invoke(
        app,
        ["dev", "json", "format", str(source), "--write"],
    )

    assert result.exit_code == 0
    assert "Updated" in result.stdout
    assert source.read_text(encoding="utf-8") == '{\n  "value": 1\n}\n'


def test_json_validate_reports_top_level_type() -> None:
    """JSON validate should name the JSON top-level value type."""
    result = runner.invoke(
        app,
        ["dev", "json", "validate"],
        input="[1, 2, 3]",
    )

    assert result.exit_code == 0
    assert "Valid JSON" in result.stdout
    assert "array" in result.stdout


def test_base64_commands_round_trip_unicode() -> None:
    """Base64 CLI commands should preserve Unicode text."""
    encoded = runner.invoke(app, ["dev", "base64", "encode", "Merhaba"])
    decoded = runner.invoke(
        app,
        ["dev", "base64", "decode", encoded.stdout.strip()],
    )

    assert encoded.exit_code == 0
    assert decoded.exit_code == 0
    assert decoded.stdout.strip() == "Merhaba"


def test_uuid_command_respects_count() -> None:
    """UUID command should print one identifier per requested item."""
    result = runner.invoke(app, ["dev", "uuid", "--count", "3"])

    assert result.exit_code == 0
    assert len(result.stdout.splitlines()) == 3


def test_password_command_respects_length() -> None:
    """Password command should print exactly the requested number of characters."""
    result = runner.invoke(app, ["dev", "password", "--length", "32"])

    assert result.exit_code == 0
    assert len(result.stdout.strip()) == 32
