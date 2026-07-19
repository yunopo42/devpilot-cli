"""Tests for secure random-value generators."""

import string
import uuid

import pytest

from devpilot.services.generators import (
    PASSWORD_SYMBOLS,
    GeneratorError,
    generate_password,
    generate_uuids,
)


def test_generate_uuids_returns_unique_uuid4_values() -> None:
    """Generated identifiers should be unique valid UUID4 values."""
    values = generate_uuids(5)

    assert len(values) == 5
    assert len(set(values)) == 5
    assert all(uuid.UUID(value).version == 4 for value in values)


def test_generate_uuids_rejects_unbounded_count() -> None:
    """UUID generation should enforce its service-level safety limit."""
    with pytest.raises(GeneratorError, match="between 1 and 100"):
        generate_uuids(101)


def test_generate_password_has_requested_length_and_all_categories() -> None:
    """Passwords should include lower, upper, digit, and symbol characters."""
    password = generate_password(24)

    assert len(password) == 24
    assert any(character in string.ascii_lowercase for character in password)
    assert any(character in string.ascii_uppercase for character in password)
    assert any(character in string.digits for character in password)
    assert any(character in PASSWORD_SYMBOLS for character in password)


def test_generate_password_rejects_unsafe_length() -> None:
    """Passwords shorter than the supported minimum should be rejected."""
    with pytest.raises(GeneratorError, match="between 8 and 256"):
        generate_password(7)
