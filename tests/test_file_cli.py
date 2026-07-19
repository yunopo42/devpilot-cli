"""Tests for the DevPilot file command group."""

from pathlib import Path

from typer.testing import CliRunner

from devpilot.cli import app

runner = CliRunner()


def test_file_info_command(tmp_path: Path) -> None:
    """File info should display readable metadata."""
    sample = tmp_path / "notes.txt"
    sample.write_text("DevPilot", encoding="utf-8")

    result = runner.invoke(app, ["file", "info", str(sample)])

    assert result.exit_code == 0
    assert "File Information" in result.stdout
    assert "notes.txt" in result.stdout
    assert ".txt" in result.stdout


def test_file_hash_command(tmp_path: Path) -> None:
    """File hash should default to SHA-256 and display the digest."""
    sample = tmp_path / "payload.txt"
    sample.write_text("hello", encoding="utf-8")

    result = runner.invoke(app, ["file", "hash", str(sample)])

    assert result.exit_code == 0
    assert "File Hash" in result.stdout
    assert "sha256" in result.stdout
    assert "2cf24dba5fb0a30e" in result.stdout


def test_file_tree_command(tmp_path: Path) -> None:
    """File tree should display direct entries."""
    folder = tmp_path / "src"
    folder.mkdir()
    (folder / "app.py").write_text("", encoding="utf-8")

    result = runner.invoke(
        app,
        ["file", "tree", str(tmp_path), "--depth", "2"],
    )

    assert result.exit_code == 0
    assert "src/" in result.stdout
    assert "app.py" in result.stdout


def test_file_largest_command(tmp_path: Path) -> None:
    """Largest files should be displayed in descending size order."""
    (tmp_path / "small.bin").write_bytes(b"1")
    (tmp_path / "large.bin").write_bytes(b"12345")

    result = runner.invoke(
        app,
        ["file", "largest", str(tmp_path), "--limit", "1"],
    )

    assert result.exit_code == 0
    assert "Largest Files" in result.stdout
    assert "large.bin" in result.stdout
    assert "small.bin" not in result.stdout
