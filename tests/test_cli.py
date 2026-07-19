"""Tests for the DevPilot command-line interface."""

from typer.testing import CliRunner

from devpilot.cli import app

runner = CliRunner()


def test_help_command() -> None:
    """The CLI should display its help text successfully."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "A modular developer toolkit for the terminal." in result.stdout


def test_version_command() -> None:
    """The version command should report the installed package version."""
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "DevPilot CLI 0.1.0" in result.stdout


def test_about_command() -> None:
    """The about command should describe the project."""
    result = runner.invoke(app, ["about"])

    assert result.exit_code == 0
    assert "Built with Python, Typer, and Rich." in result.stdout


def test_doctor_command() -> None:
    """The doctor command should display the core environment checks."""
    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "DevPilot Doctor" in result.stdout
    assert "Python" in result.stdout
    assert "Operating system" in result.stdout
    assert "Package" in result.stdout


def test_debug_option_is_global() -> None:
    """The debug option should be accepted before a subcommand."""
    result = runner.invoke(app, ["--debug", "doctor"])

    assert result.exit_code == 0
