"""Tests for the DevPilot command-line interface."""

from typer.testing import CliRunner

from devpilot.cli import app

runner = CliRunner()


def test_help_command() -> None:
    """The CLI should display its help text successfully."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "A modular developer toolkit for the terminal." in result.stdout
