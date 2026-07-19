"""Safe, read-only file-system operations."""

import hashlib
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from ..core.errors import DevPilotError
from ..models.file import FileInfo, HashResult, LargestFile, TreeEntry

HASH_CHUNK_SIZE = 1024 * 1024
SUPPORTED_HASH_ALGORITHMS = frozenset({"sha256", "sha512", "blake2b"})


class FileOperationError(DevPilotError):
    """Raised when a safe file operation cannot be completed."""


def resolve_path(path: Path) -> Path:
    """Resolve an existing path without accepting a symbolic-link target."""
    expanded = path.expanduser()
    if expanded.is_symlink():
        raise FileOperationError(f"Symbolic links are not supported: {path}")

    try:
        return expanded.resolve(strict=True)
    except FileNotFoundError as error:
        raise FileOperationError(f"Path does not exist: {path}") from error
    except OSError as error:
        raise FileOperationError(f"Path could not be resolved: {path}") from error


def get_file_info(path: Path) -> FileInfo:
    """Read metadata for one regular file or directory."""
    resolved = resolve_path(path)
    try:
        stat = resolved.stat()
    except OSError as error:
        raise FileOperationError(f"Metadata could not be read: {resolved}") from error

    is_file = resolved.is_file()
    return FileInfo(
        path=str(resolved),
        name=resolved.name or str(resolved),
        kind="file" if is_file else "directory",
        size_bytes=stat.st_size if is_file else None,
        extension=resolved.suffix or None if is_file else None,
        modified_at=datetime.fromtimestamp(stat.st_mtime)
        .astimezone()
        .isoformat(timespec="seconds"),
    )


def hash_file(path: Path, algorithm: str = "sha256") -> HashResult:
    """Hash a regular file incrementally without loading it all into memory."""
    normalized_algorithm = algorithm.lower()
    if normalized_algorithm not in SUPPORTED_HASH_ALGORITHMS:
        supported = ", ".join(sorted(SUPPORTED_HASH_ALGORITHMS))
        raise FileOperationError(
            f"Unsupported hash algorithm: {algorithm}. Choose from: {supported}."
        )

    resolved = resolve_path(path)
    if not resolved.is_file():
        raise FileOperationError(f"A regular file is required: {resolved}")

    digest = hashlib.new(normalized_algorithm)
    size_bytes = 0
    try:
        with resolved.open("rb") as file_handle:
            while chunk := file_handle.read(HASH_CHUNK_SIZE):
                digest.update(chunk)
                size_bytes += len(chunk)
    except OSError as error:
        raise FileOperationError(f"File could not be read: {resolved}") from error

    return HashResult(
        path=str(resolved),
        algorithm=normalized_algorithm,
        digest=digest.hexdigest(),
        size_bytes=size_bytes,
    )


def _iter_tree(
    directory: Path,
    root: Path,
    depth: int,
    max_depth: int,
) -> Iterator[TreeEntry]:
    """Yield directory entries depth-first up to a safe depth boundary."""
    if depth > max_depth:
        return

    try:
        children = sorted(
            directory.iterdir(),
            key=lambda item: (item.is_file(), item.name.lower()),
        )
    except OSError as error:
        raise FileOperationError(f"Directory could not be read: {directory}") from error

    for child in children:
        if child.is_symlink():
            continue

        is_directory = child.is_dir()
        yield TreeEntry(
            relative_path=child.relative_to(root).as_posix(),
            kind="directory" if is_directory else "file",
            depth=depth,
            size_bytes=child.stat().st_size if child.is_file() else None,
        )
        if is_directory:
            yield from _iter_tree(child, root, depth + 1, max_depth)


def build_tree(path: Path, max_depth: int = 3) -> tuple[TreeEntry, ...]:
    """Return a bounded, deterministic directory tree."""
    if max_depth < 0:
        raise FileOperationError("Tree depth cannot be negative.")

    root = resolve_path(path)
    if not root.is_dir():
        raise FileOperationError(f"A directory is required: {root}")

    return tuple(_iter_tree(root, root, depth=1, max_depth=max_depth))


def _iter_regular_files(directory: Path) -> Iterator[Path]:
    """Yield regular files recursively without following symbolic links."""
    try:
        children = directory.iterdir()
    except OSError as error:
        raise FileOperationError(f"Directory could not be read: {directory}") from error

    for child in children:
        if child.is_symlink():
            continue
        if child.is_dir():
            yield from _iter_regular_files(child)
        elif child.is_file():
            yield child


def find_largest_files(path: Path, limit: int = 10) -> tuple[LargestFile, ...]:
    """Return the largest regular files below a directory."""
    if limit < 1:
        raise FileOperationError("Result limit must be at least 1.")

    root = resolve_path(path)
    if not root.is_dir():
        raise FileOperationError(f"A directory is required: {root}")

    files: list[LargestFile] = []
    try:
        for file_path in _iter_regular_files(root):
            files.append(
                LargestFile(
                    path=file_path.relative_to(root).as_posix(),
                    size_bytes=file_path.stat().st_size,
                )
            )
    except OSError as error:
        raise FileOperationError("A file entry could not be inspected.") from error

    files.sort(key=lambda item: (-item.size_bytes, item.path.lower()))
    return tuple(files[:limit])
