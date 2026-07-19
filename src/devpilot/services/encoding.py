"""Text encoding and decoding helpers."""

import base64
import binascii

from ..core.errors import DevPilotError


class EncodingToolError(DevPilotError):
    """Raised when encoded text cannot be processed."""


def encode_base64(text: str) -> str:
    """Encode Unicode text as standard Base64."""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def decode_base64(text: str) -> str:
    """Decode strict Base64 data into UTF-8 text."""
    try:
        decoded = base64.b64decode(text, validate=True)
    except (binascii.Error, ValueError) as error:
        raise EncodingToolError("Input is not valid Base64 data.") from error

    try:
        return decoded.decode("utf-8")
    except UnicodeDecodeError as error:
        raise EncodingToolError("Decoded data is not valid UTF-8 text.") from error
