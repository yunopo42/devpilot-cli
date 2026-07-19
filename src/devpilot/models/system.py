"""Structured results returned by the system information service."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CpuInfo:
    """CPU capacity and current utilization."""

    physical_cores: int | None
    logical_cores: int | None
    usage_percent: float


@dataclass(frozen=True, slots=True)
class MemoryInfo:
    """Physical memory capacity and utilization in bytes."""

    total_bytes: int
    available_bytes: int
    used_bytes: int
    usage_percent: float


@dataclass(frozen=True, slots=True)
class DiskInfo:
    """Disk capacity and utilization in bytes."""

    path: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    usage_percent: float


@dataclass(frozen=True, slots=True)
class SystemInfo:
    """Cross-platform summary of the local system."""

    operating_system: str
    operating_system_version: str
    architecture: str
    hostname: str
    python_version: str
    cpu: CpuInfo
    memory: MemoryInfo
    disk: DiskInfo
