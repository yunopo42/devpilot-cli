"""Structured results returned by file services."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FileInfo:
    """Metadata describing one file-system entry."""

    path: str
    name: str
    kind: str
    size_bytes: int | None
    extension: str | None
    modified_at: str


@dataclass(frozen=True, slots=True)
class HashResult:
    """Digest calculated for one regular file."""

    path: str
    algorithm: str
    digest: str
    size_bytes: int


@dataclass(frozen=True, slots=True)
class TreeEntry:
    """One entry in a bounded directory tree."""

    relative_path: str
    kind: str
    depth: int
    size_bytes: int | None


@dataclass(frozen=True, slots=True)
class LargestFile:
    """A regular file included in a size-ranked result."""

    path: str
    size_bytes: int
