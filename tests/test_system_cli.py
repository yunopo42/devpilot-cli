"""Tests for the DevPilot system command group."""

import json

from typer.testing import CliRunner

import devpilot.commands.system as system_commands
from devpilot.cli import app
from devpilot.models.system import CpuInfo, DiskInfo, MemoryInfo, SystemInfo

runner = CliRunner()


def sample_system_info() -> SystemInfo:
    """Return stable system data for CLI presentation tests."""
    return SystemInfo(
        operating_system="TestOS",
        operating_system_version="1.0",
        architecture="x86-test",
        hostname="test-host",
        python_version="3.13.3",
        cpu=CpuInfo(physical_cores=4, logical_cores=8, usage_percent=12.5),
        memory=MemoryInfo(
            total_bytes=16_000,
            available_bytes=10_000,
            used_bytes=6_000,
            usage_percent=37.5,
        ),
        disk=DiskInfo(
            path="/test",
            total_bytes=1_000,
            used_bytes=400,
            free_bytes=600,
            usage_percent=40.0,
        ),
    )


def test_system_info_table(monkeypatch) -> None:
    """System info should use a readable table by default."""
    monkeypatch.setattr(system_commands, "get_system_info", sample_system_info)

    result = runner.invoke(app, ["system", "info"])

    assert result.exit_code == 0
    assert "DevPilot System Information" in result.stdout
    assert "TestOS 1.0" in result.stdout
    assert "37.5%" in result.stdout


def test_system_info_json(monkeypatch) -> None:
    """System info should provide structured JSON for automation."""
    monkeypatch.setattr(system_commands, "get_system_info", sample_system_info)

    result = runner.invoke(app, ["system", "info", "--output", "json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["hostname"] == "test-host"
    assert payload["cpu"]["logical_cores"] == 8
    assert payload["memory"]["total_bytes"] == 16_000


def test_cpu_command(monkeypatch) -> None:
    """The CPU command should display core counts and utilization."""
    monkeypatch.setattr(
        system_commands,
        "get_cpu_info",
        lambda: sample_system_info().cpu,
    )

    result = runner.invoke(app, ["system", "cpu"])

    assert result.exit_code == 0
    assert "CPU Information" in result.stdout
    assert "Physical cores" in result.stdout
    assert "12.5%" in result.stdout


def test_memory_command(monkeypatch) -> None:
    """The memory command should display capacity and utilization."""
    monkeypatch.setattr(
        system_commands,
        "get_memory_info",
        lambda: sample_system_info().memory,
    )

    result = runner.invoke(app, ["system", "memory"])

    assert result.exit_code == 0
    assert "Memory Information" in result.stdout
    assert "37.5%" in result.stdout


def test_disk_command(monkeypatch) -> None:
    """The disk command should display path, capacity, and utilization."""
    monkeypatch.setattr(
        system_commands,
        "get_disk_info",
        lambda: sample_system_info().disk,
    )

    result = runner.invoke(app, ["system", "disk"])

    assert result.exit_code == 0
    assert "Disk Information" in result.stdout
    assert "/test" in result.stdout
    assert "40.0%" in result.stdout


def test_format_bytes_uses_binary_units() -> None:
    """Byte values should be formatted consistently for people."""
    assert system_commands.format_bytes(1_024) == "1.0 KiB"
    assert system_commands.format_bytes(1_073_741_824) == "1.0 GiB"
