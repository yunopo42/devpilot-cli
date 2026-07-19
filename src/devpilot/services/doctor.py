"""Environment checks used by the ``devpilot doctor`` command."""

import platform
import sys
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DoctorCheck:
    """Result of one environment check."""

    name: str
    passed: bool
    details: str


def run_doctor_checks() -> tuple[DoctorCheck, ...]:
    """Inspect the minimum environment required by DevPilot."""
    python_version = platform.python_version()
    python_supported = sys.version_info >= (3, 11)

    return (
        DoctorCheck(
            name="Python",
            passed=python_supported,
            details=f"Python {python_version} (requires 3.11+)",
        ),
        DoctorCheck(
            name="Operating system",
            passed=bool(platform.system()),
            details=f"{platform.system()} {platform.release()}",
        ),
        DoctorCheck(
            name="Package",
            passed=True,
            details="DevPilot CLI is installed and importable",
        ),
    )
