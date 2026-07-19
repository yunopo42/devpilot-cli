"""Everyday developer utility commands."""

from pathlib import Path

import typer

from ..core.console import console
from ..core.theme import active_palette
from ..services.encoding import decode_base64, encode_base64
from ..services.generators import generate_password, generate_uuids
from ..services.json_tools import (
    JsonToolError,
    format_json,
    parse_json,
    read_text_file,
    write_text_atomic,
)

dev_app = typer.Typer(
    help="Format, encode, and generate common developer values.",
    no_args_is_help=True,
)
json_app = typer.Typer(help="Format and validate JSON data.", no_args_is_help=True)
base64_app = typer.Typer(help="Encode and decode Base64 text.", no_args_is_help=True)

dev_app.add_typer(json_app, name="json")
dev_app.add_typer(base64_app, name="base64")


def read_input(path: Path | None) -> str:
    """Read UTF-8 input from a file or standard input."""
    if path is not None:
        return read_text_file(path)

    text = typer.get_text_stream("stdin").read()
    if not text:
        raise JsonToolError("No input received. Provide a file or pipe JSON to stdin.")
    return text


def json_type_name(data: object) -> str:
    """Return the JSON vocabulary name for a parsed Python value."""
    if data is None:
        return "null"
    if isinstance(data, bool):
        return "boolean"
    if isinstance(data, dict):
        return "object"
    if isinstance(data, list):
        return "array"
    if isinstance(data, str):
        return "string"
    return "number"


@json_app.command("format")
def json_format_command(
    path: Path | None = typer.Argument(
        None,
        help="JSON file. Omit it to read from stdin.",
    ),
    write: bool = typer.Option(
        False,
        "--write",
        help="Atomically replace the input file with formatted JSON.",
    ),
    indent: int = typer.Option(
        2,
        "--indent",
        min=0,
        max=8,
        help="Number of spaces used for indentation.",
    ),
    sort_keys: bool = typer.Option(
        False,
        "--sort-keys",
        help="Sort object keys alphabetically.",
    ),
) -> None:
    """Format JSON from a UTF-8 file or standard input."""
    if write and path is None:
        raise JsonToolError("--write requires an input file path.")

    formatted = format_json(read_input(path), indent=indent, sort_keys=sort_keys)
    if write:
        assert path is not None
        write_text_atomic(path, formatted)
        palette = active_palette()
        console.print(f"[{palette.success}]Updated:[/{palette.success}] {path}")
        return

    console.print(formatted, markup=False, soft_wrap=True, end="")


@json_app.command("validate")
def json_validate_command(
    path: Path | None = typer.Argument(
        None,
        help="JSON file. Omit it to read from stdin.",
    ),
) -> None:
    """Validate JSON and report its top-level value type."""
    data = parse_json(read_input(path))
    value_type = json_type_name(data)
    palette = active_palette()
    console.print(
        f"[{palette.success}]Valid JSON[/{palette.success}] "
        f"(top-level type: {value_type})"
    )


@base64_app.command("encode")
def base64_encode_command(
    text: str = typer.Argument(..., help="UTF-8 text to encode."),
) -> None:
    """Encode UTF-8 text as standard Base64."""
    console.print(encode_base64(text), markup=False, soft_wrap=True)


@base64_app.command("decode")
def base64_decode_command(
    text: str = typer.Argument(..., help="Standard Base64 text to decode."),
) -> None:
    """Decode standard Base64 into UTF-8 text."""
    console.print(decode_base64(text), markup=False, soft_wrap=True)


@dev_app.command("uuid")
def uuid_command(
    count: int = typer.Option(
        1,
        "--count",
        "-n",
        min=1,
        max=100,
        help="Number of UUID4 values to generate.",
    ),
) -> None:
    """Generate random UUID4 values."""
    for value in generate_uuids(count):
        console.print(value, markup=False)


@dev_app.command("password")
def password_command(
    length: int = typer.Option(
        24,
        "--length",
        "-l",
        min=8,
        max=256,
        help="Password length.",
    ),
) -> None:
    """Generate a cryptographically secure mixed-character password."""
    console.print(generate_password(length), markup=False)
