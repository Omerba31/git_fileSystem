import ctypes
import os
from pathlib import Path
from typing import IO, Tuple, overload

import _libcaf
from _libcaf import (
    Commit,
    computeHash,
    Blob,
    TreeRecord,
    Tree,
    TreeRecordType
)


def compute_hash(filename: str | Path) -> str:
    if isinstance(filename, Path):
        filename = str(filename)

    try:
        result, hash_output = _libcaf.compute_hash(filename)
    except UnicodeDecodeError:
        raise FileNotFoundError(f"File '{filename}' not found.")

    if result == -1:
        raise FileNotFoundError(f"File '{filename}' not found.")
    if result != 0:
        errno = ctypes.get_errno()
        error_message = f"Failed to compute SHA1 for file '{filename}'. Error code: {errno}, Description: {os.strerror(errno)}"
        raise OSError(errno, error_message)

    return hash_output


def open_content(root_dir, hash_value) -> IO:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    fd = _libcaf.open_content(root_dir, hash_value)

    if fd == -1:
        raise OSError(f"Failed to open content with hash '{hash_value}' in directory '{root_dir}'")

    return os.fdopen(fd, 'r')


def delete_content(root_dir: str | Path, hash_value: str) -> None:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    _libcaf.delete_content(root_dir, hash_value)


@overload
def save_content(root_dir: str | Path, filename: str | Path) -> None:
    ...


@overload
def save_content(root_dir: str | Path, hash_value: str, flags: int) -> Tuple[IO, Path]:
    ...


def save_content(root_dir: str | Path, filename_or_hash: str | Path, flags: int = None) -> \
        Tuple[IO, Path] | None:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    if flags is None:
        if isinstance(filename_or_hash, Path):
            filename_or_hash = str(filename_or_hash)

        _libcaf.save_content(root_dir, filename_or_hash)
    else:
        if isinstance(filename_or_hash, Path):
            raise ValueError("Filename cannot be a Path object when saving content with hash and flags")

        result, fd, blob_path = _libcaf.save_content(root_dir, filename_or_hash, flags)

        if result != 0:
            raise OSError(f"Failed to save content with hash '{filename_or_hash}' in directory '{root_dir}'")

        return os.fdopen(fd, 'w'), Path(blob_path)


def save_commit(root_dir: str | Path, commit) -> None:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    result = _libcaf.save_commit(root_dir, commit)

    if result != 0:
        raise OSError(f"Failed to save commit in directory '{root_dir}'")


def load_commit(root_dir: str | Path, hash_value) -> Commit:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    result, commit = _libcaf.load_commit(root_dir, hash_value)

    if result != 0:
        raise OSError(f"Failed to load commit with hash '{hash_value}' in directory '{root_dir}'")

    return commit

def save_tree(root_dir: str | Path, tree: Tree) -> None:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    result = _libcaf.save_tree(root_dir, tree)

    if result != 0:
        raise OSError(f"Failed to save Tree in directory '{root_dir}'")


def load_tree(root_dir: str | Path, hash_value) -> Tree:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    result, tree = _libcaf.load_tree(root_dir, hash_value)

    if result != 0:
        raise OSError(f"Failed to load Tree with hash '{hash_value}' in directory '{root_dir}'")

    return tree


__all__ = [
    'compute_hash',
    'save_content',
    'save_commit',
    'load_commit',
    'save_tree',
    'load_tree',
    'open_content',
    'delete_content',
    'Commit',
    'computeHash',
    'Blob',
    'TreeRecord',
    'Tree',
    'TreeRecordType'
]
