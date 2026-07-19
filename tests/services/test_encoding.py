"""Tests for text encoding services."""

import pytest

from devpilot.services.encoding import (
    EncodingToolError,
    decode_base64,
    encode_base64,
)


def test_base64_round_trip_preserves_unicode() -> None:
    """Unicode text should survive a Base64 encode/decode round trip."""
    text = "Merhaba dünya 👋"

    assert decode_base64(encode_base64(text)) == text


def test_decode_base64_rejects_invalid_data() -> None:
    """Malformed Base64 should become a clean application error."""
    with pytest.raises(EncodingToolError, match="not valid Base64"):
        decode_base64("not-base64!")


def test_decode_base64_rejects_non_utf8_bytes() -> None:
    """Decoded binary data should not be misrepresented as UTF-8 text."""
    with pytest.raises(EncodingToolError, match="not valid UTF-8"):
        decode_base64("/w==")
