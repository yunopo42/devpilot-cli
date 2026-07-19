"""System information commands."""

import json
from dataclasses import asdict
from enum import StrEnum

import typer
from rich.table import Table

from ..core.console import console
from ..models.system import CpuInfo, DiskInfo, MemoryInfo, SystemInfo
from ..services.system import (
    get_cpu_info,
    get_disk_info,
    get_memory_info,
    get_system_info,
)


class OutputFormat(StrEnum):
    """Supported command output formats."""

    TABLE = "table"
    JSON = "json"


system_app = typer.Typer(
    help="Inspect local CPU, memory, disk, and operating-system information.",
    no_args_is_help=True,
)


def format_bytes(value: int) -> str:
    """Format a byte count using binary units."""
    size = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(size) < 1024.0 or unit == "TiB":
            return f"{size:.1f} {unit}"
        size /= 1024.0

    raise AssertionError("unreachable")


def render_cpu(cpu: CpuInfo) -> None:
    """Render CPU information as a Rich table."""
    table = Table(title="CPU Information")
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_row("Physical cores", str(cpu.physical_cores or "Unknown"))
    table.add_row("Logical cores", str(cpu.logical_cores or "Unknown"))
    table.add_row("Usage", f"{cpu.usage_percent:.1f}%")
    console.print(table)


def render_memory(memory: MemoryInfo) -> None:
    """Render memory information as a Rich table."""
    table = Table(title="Memory Information")
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_row("Total", format_bytes(memory.total_bytes))
    table.add_row("Available", format_bytes(memory.available_bytes))
    table.add_row("Used", format_bytes(memory.used_bytes))
    table.add_row("Usage", f"{memory.usage_percent:.1f}%")
    console.print(table)


def render_disk(disk: DiskInfo) -> None:
    """Render disk information as a Rich table."""
    table = Table(title="Disk Information")
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_row("Path", disk.path)
    table.add_row("Total", format_bytes(disk.total_bytes))
    table.add_row("Used", format_bytes(disk.used_bytes))
    table.add_row("Free", format_bytes(disk.free_bytes))
    table.add_row("Usage", f"{disk.usage_percent:.1f}%")
    console.print(table)


def render_system_info(system: SystemInfo) -> None:
    """Render a complete system summary as a Rich table."""
    table = Table(title="DevPilot System Information")
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_row(
        "Operating system",
        f"{system.operating_system} {system.operating_system_version}",
    )
    table.add_row("Architecture", system.architecture)
    table.add_row("Hostname", system.hostname)
    table.add_row("Python", system.python_version)
    table.add_row("CPU usage", f"{system.cpu.usage_percent:.1f}%")
    table.add_row("Memory usage", f"{system.memory.usage_percent:.1f}%")
    table.add_row("Disk usage", f"{system.disk.usage_percent:.1f}%")
    console.print(table)


@system_app.command("info")
def info_command(
    output: OutputFormat = typer.Option(
        OutputFormat.TABLE,
        "--output",
        "-o",
        case_sensitive=False,
        help="Choose table or json output.",
    ),
) -> None:
    """Show a summary of the local system."""
    system = get_system_info()
    if output is OutputFormat.JSON:
        console.print_json(json.dumps(asdict(system)))
        return

    render_system_info(system)


@system_app.command("cpu")
def cpu_command() -> None:
    """Show CPU core counts and current utilization."""
    render_cpu(get_cpu_info())


@system_app.command("memory")
def memory_command() -> None:
    """Show physical memory capacity and utilization."""
    render_memory(get_memory_info())


@system_app.command("disk")
def disk_command() -> None:
    """Show system disk capacity and utilization."""
    render_disk(get_disk_info())
