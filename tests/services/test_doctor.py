"""Tests for the environment doctor service."""

from devpilot.services.doctor import run_doctor_checks


def test_doctor_checks_have_useful_results() -> None:
    """Every core environment check should include a readable result."""
    checks = run_doctor_checks()

    assert {check.name for check in checks} == {
        "Python",
        "Operating system",
        "Package",
    }
    assert all(check.details for check in checks)
    assert all(check.passed for check in checks)
