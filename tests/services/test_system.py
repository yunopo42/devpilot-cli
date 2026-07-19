"""Tests for cross-platform system information collection."""

from types import SimpleNamespace

import devpilot.services.system as system_service
from devpilot.models.system import CpuInfo, DiskInfo, MemoryInfo


def test_get_cpu_info(monkeypatch) -> None:
    """CPU information should preserve core counts and utilization."""
    monkeypatch.setattr(
        system_service.psutil,
        "cpu_count",
        lambda *, logical: 8 if logical else 4,
    )
    monkeypatch.setattr(
        system_service.psutil,
        "cpu_percent",
        lambda *, interval: 12.5 if interval == 0.1 else 0.0,
    )

    cpu = system_service.get_cpu_info()

    assert cpu.physical_cores == 4
    assert cpu.logical_cores == 8
    assert cpu.usage_percent == 12.5


def test_get_memory_info(monkeypatch) -> None:
    """Memory information should use byte values returned by psutil."""
    memory_result = SimpleNamespace(
        total=16_000,
        available=10_000,
        used=6_000,
        percent=37.5,
    )
    monkeypatch.setattr(system_service.psutil, "virtual_memory", lambda: memory_result)

    memory = system_service.get_memory_info()

    assert memory.total_bytes == 16_000
    assert memory.available_bytes == 10_000
    assert memory.used_bytes == 6_000
    assert memory.usage_percent == 37.5


def test_get_disk_info(monkeypatch) -> None:
    """Disk information should report the inspected path and byte values."""
    disk_result = SimpleNamespace(
        total=1_000,
        used=400,
        free=600,
        percent=40.0,
    )
    monkeypatch.setattr(
        system_service.psutil,
        "disk_usage",
        lambda path: disk_result,
    )

    disk = system_service.get_disk_info("/test")

    assert disk.path == "/test"
    assert disk.total_bytes == 1_000
    assert disk.used_bytes == 400
    assert disk.free_bytes == 600
    assert disk.usage_percent == 40.0


def test_get_system_info_combines_platform_and_resource_data(monkeypatch) -> None:
    """The full summary should combine platform data with service results."""
    monkeypatch.setattr(system_service.platform, "system", lambda: "TestOS")
    monkeypatch.setattr(system_service.platform, "release", lambda: "1.0")
    monkeypatch.setattr(system_service.platform, "machine", lambda: "x86-test")
    monkeypatch.setattr(system_service.platform, "node", lambda: "test-host")
    monkeypatch.setattr(system_service.platform, "python_version", lambda: "3.13.3")
    monkeypatch.setattr(
        system_service,
        "get_cpu_info",
        lambda: CpuInfo(physical_cores=4, logical_cores=8, usage_percent=12.5),
    )
    monkeypatch.setattr(
        system_service,
        "get_memory_info",
        lambda: MemoryInfo(
            total_bytes=16_000,
            available_bytes=10_000,
            used_bytes=6_000,
            usage_percent=37.5,
        ),
    )
    monkeypatch.setattr(
        system_service,
        "get_disk_info",
        lambda: DiskInfo(
            path="/test",
            total_bytes=1_000,
            used_bytes=400,
            free_bytes=600,
            usage_percent=40.0,
        ),
    )

    system = system_service.get_system_info()

    assert system.operating_system == "TestOS"
    assert system.operating_system_version == "1.0"
    assert system.architecture == "x86-test"
    assert system.hostname == "test-host"
    assert system.python_version == "3.13.3"
    assert system.cpu.logical_cores == 8
    assert system.memory.usage_percent == 37.5
    assert system.disk.path == "/test"
