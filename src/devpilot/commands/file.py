"""Read-only file information commands."""

from enum import StrEnum
from pathlib import Path, PurePosixPath

import typer
from rich.table import Table
from rich.tree import Tree

from ..core.console import console
from ..core.formatting import format_bytes
from ..models.file import FileInfo, HashResult, LargestFile, TreeEntry
from ..services.file import build_tree, find_largest_files, get_file_info, hash_file


class HashAlgorithm(StrEnum):
    """Hash algorithms intentionally supported by DevPilot."""

    SHA256 = "sha256"
    SHA512 = "sha512"
    BLAKE2B = "blake2b"


file_app = typer.Typer(
    help="Inspect files and directories with safe, read-only operations.",
    no_args_is_help=True,
)


def render_file_info(info: FileInfo) -> None:
    """Render file metadata as a Rich table."""
    table = Table(title="File Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    table.add_row("Path", info.path)
    table.add_row("Name", info.name)
    table.add_row("Type", info.kind)
    table.add_row(
        "Size",
        format_bytes(info.size_bytes) if info.size_bytes is not None else "—",
    )
    table.add_row("Extension", info.extension or "—")
    table.add_row("Modified", info.modified_at)
    console.print(table)


def render_hash(result: HashResult) -> None:
    """Render a file digest and its context."""
    table = Table(title="File Hash")
    table.add_column("Property", style="cyan")
    table.add_column("Value")
    table.add_row("Path", result.path)
    table.add_row("Algorithm", result.algorithm)
    table.add_row("Size", format_bytes(result.size_bytes))
    console.print(table)
    console.print(f"[bold cyan]Digest:[/bold cyan] {result.digest}", soft_wrap=True)


def render_tree(root: Path, entries: tuple[TreeEntry, ...]) -> None:
    """Render bounded tree entries as a Rich tree."""
    tree = Tree(f"[bold cyan]{root}[/bold cyan]")
    directory_nodes = {".": tree}

    for entry in entries:
        relative = PurePosixPath(entry.relative_path)
        parent = directory_nodes.get(relative.parent.as_posix(), tree)
        if entry.kind == "directory":
            node = parent.add(f"[bold]{relative.name}/[/bold]")
            directory_nodes[relative.as_posix()] = node
        else:
            size = format_bytes(entry.size_bytes or 0)
            parent.add(f"{relative.name} [dim]({size})[/dim]")

    console.print(tree)


def render_largest(files: tuple[LargestFile, ...]) -> None:
    """Render size-ranked files as a Rich table."""
    table = Table(title="Largest Files")
    table.add_column("Rank", justify="right", style="cyan")
    table.add_column("Path")
    table.add_column("Size", justify="right")

    for rank, item in enumerate(files, start=1):
        table.add_row(str(rank), item.path, format_bytes(item.size_bytes))

    console.print(table)


@file_app.command("info")
def info_command(
    path: Path = typer.Argument(..., help="File or directory to inspect."),
) -> None:
    """Show metadata for a file or directory."""
    render_file_info(get_file_info(path))


@file_app.command("hash")
def hash_command(
    path: Path = typer.Argument(..., help="Regular file to hash."),
    algorithm: HashAlgorithm = typer.Option(
        HashAlgorithm.SHA256,
        "--algorithm",
        "-a",
        case_sensitive=False,
        help="Hash algorithm to use.",
    ),
) -> None:
    """Calculate a cryptographic digest without loading the file into memory."""
    render_hash(hash_file(path, algorithm.value))


@file_app.command("tree")
def tree_command(
    path: Path = typer.Argument(Path("."), help="Directory to display."),
    depth: int = typer.Option(
        3,
        "--depth",
        "-d",
        min=0,
        max=20,
        help="Maximum directory depth to display.",
    ),
) -> None:
    """Display a directory tree without following symbolic links."""
    render_tree(path, build_tree(path, max_depth=depth))


@file_app.command("largest")
def largest_command(
    path: Path = typer.Argument(Path("."), help="Directory to search."),
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        min=1,
        max=100,
        help="Maximum number of files to display.",
    ),
) -> None:
    """List the largest files without following symbolic links."""
    render_largest(find_largest_files(path, limit=limit))
