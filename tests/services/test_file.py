"""Tests for safe, read-only file services."""

import hashlib
from pathlib import Path

import pytest

from devpilot.services.file import (
    FileOperationError,
    build_tree,
    find_largest_files,
    get_file_info,
    hash_file,
)


def test_get_file_info_for_regular_file(tmp_path: Path) -> None:
    """File metadata should include type, extension, and exact byte size."""
    sample = tmp_path / "sample.txt"
    sample.write_text("hello", encoding="utf-8")

    info = get_file_info(sample)

    assert info.name == "sample.txt"
    assert info.kind == "file"
    assert info.size_bytes == 5
    assert info.extension == ".txt"
    assert info.modified_at


def test_get_file_info_rejects_missing_path(tmp_path: Path) -> None:
    """Missing paths should become safe application errors."""
    with pytest.raises(FileOperationError, match="Path does not exist"):
        get_file_info(tmp_path / "missing.txt")


@pytest.mark.parametrize("algorithm", ["sha256", "sha512", "blake2b"])
def test_hash_file_matches_hashlib(tmp_path: Path, algorithm: str) -> None:
    """Streaming hashes should match Python's trusted hashlib output."""
    content = b"DevPilot streaming hash test"
    sample = tmp_path / "payload.bin"
    sample.write_bytes(content)

    result = hash_file(sample, algorithm)

    expected = hashlib.new(algorithm, content).hexdigest()
    assert result.algorithm == algorithm
    assert result.digest == expected
    assert result.size_bytes == len(content)


def test_hash_file_rejects_directory(tmp_path: Path) -> None:
    """Hashing should accept regular files only."""
    with pytest.raises(FileOperationError, match="regular file"):
        hash_file(tmp_path)


def test_build_tree_respects_depth(tmp_path: Path) -> None:
    """Tree traversal should stop below the requested maximum depth."""
    nested = tmp_path / "level-one" / "level-two"
    nested.mkdir(parents=True)
    (tmp_path / "root.txt").write_text("root", encoding="utf-8")
    (nested / "deep.txt").write_text("deep", encoding="utf-8")

    entries = build_tree(tmp_path, max_depth=1)
    paths = {entry.relative_path for entry in entries}

    assert "level-one" in paths
    assert "root.txt" in paths
    assert "level-one/level-two" not in paths
    assert "level-one/level-two/deep.txt" not in paths


def test_find_largest_files_sorts_and_limits_results(tmp_path: Path) -> None:
    """Largest-file results should be descending and respect the limit."""
    (tmp_path / "small.bin").write_bytes(b"1")
    (tmp_path / "large.bin").write_bytes(b"12345")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "medium.bin").write_bytes(b"123")

    files = find_largest_files(tmp_path, limit=2)

    assert [(item.path, item.size_bytes) for item in files] == [
        ("large.bin", 5),
        ("nested/medium.bin", 3),
    ]
