"""Secure random-value generators."""

import secrets
import string
import uuid

from ..core.errors import DevPilotError

PASSWORD_SYMBOLS = "!@#$%^&*()-_=+"


class GeneratorError(DevPilotError):
    """Raised when a generator receives an unsafe request."""


def generate_uuids(count: int = 1) -> tuple[str, ...]:
    """Generate a bounded collection of random UUID4 values."""
    if not 1 <= count <= 100:
        raise GeneratorError("UUID count must be between 1 and 100.")
    return tuple(str(uuid.uuid4()) for _ in range(count))


def generate_password(length: int = 24) -> str:
    """Generate a cryptographically secure password with mixed categories."""
    if not 8 <= length <= 256:
        raise GeneratorError("Password length must be between 8 and 256.")

    categories = (
        string.ascii_lowercase,
        string.ascii_uppercase,
        string.digits,
        PASSWORD_SYMBOLS,
    )
    password = [secrets.choice(category) for category in categories]
    alphabet = "".join(categories)
    password.extend(secrets.choice(alphabet) for _ in range(length - len(password)))
    secrets.SystemRandom().shuffle(password)
    return "".join(password)
