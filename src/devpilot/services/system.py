"""Cross-platform system information collection."""

import platform
from pathlib import Path

import psutil

from ..core.errors import DevPilotError
from ..models.system import CpuInfo, DiskInfo, MemoryInfo, SystemInfo


class SystemInspectionError(DevPilotError):
    """Raised when local system information cannot be collected."""


def get_cpu_info() -> CpuInfo:
    """Collect CPU core counts and current utilization."""
    return CpuInfo(
        physical_cores=psutil.cpu_count(logical=False),
        logical_cores=psutil.cpu_count(logical=True),
        usage_percent=psutil.cpu_percent(interval=0.1),
    )


def get_memory_info() -> MemoryInfo:
    """Collect physical memory capacity and current utilization."""
    memory = psutil.virtual_memory()
    return MemoryInfo(
        total_bytes=memory.total,
        available_bytes=memory.available,
        used_bytes=memory.used,
        usage_percent=memory.percent,
    )


def get_system_disk_path() -> str:
    """Return a usable root path for the current platform."""
    return Path.home().anchor or "/"


def get_disk_info(path: str | None = None) -> DiskInfo:
    """Collect disk capacity and current utilization for a path."""
    inspected_path = path or get_system_disk_path()
    try:
        disk = psutil.disk_usage(inspected_path)
    except (OSError, psutil.Error) as error:
        raise SystemInspectionError(
            f"Disk information could not be read for {inspected_path}."
        ) from error

    return DiskInfo(
        path=inspected_path,
        total_bytes=disk.total,
        used_bytes=disk.used,
        free_bytes=disk.free,
        usage_percent=disk.percent,
    )


def get_system_info() -> SystemInfo:
    """Collect a complete, cross-platform system summary."""
    return SystemInfo(
        operating_system=platform.system() or "Unknown",
        operating_system_version=platform.release() or "Unknown",
        architecture=platform.machine() or "Unknown",
        hostname=platform.node() or "Unknown",
        python_version=platform.python_version(),
        cpu=get_cpu_info(),
        memory=get_memory_info(),
        disk=get_disk_info(),
    )
