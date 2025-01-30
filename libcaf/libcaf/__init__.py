import ctypes
import os
from pathlib import Path
from typing import IO, Tuple, overload

import _libcaf
from _libcaf import (
    Commit,
    hash_object,
    Blob,
    TreeRecord,
    Tree,
    TreeRecordType
)


def hash_file(filename: str | Path) -> str:
    if isinstance(filename, Path):
        filename = str(filename)

    return _libcaf.hash_file(filename)

def open_content_for_reading(root_dir, hash_value:str) -> IO:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    fd = _libcaf.open_content_for_reading(root_dir, hash_value)

    return os.fdopen(fd, 'r')

def open_content_for_saving(root_dir, hash_value: str) -> IO:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    fd = _libcaf.open_content_for_saving(root_dir, hash_value)

    return os.fdopen(fd, 'w')

def delete_content(root_dir: str | Path, hash_value: str) -> None:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    _libcaf.delete_content(root_dir, hash_value)

def save_file_content(root_dir: str | Path, file_path: str | Path) -> Blob:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    if isinstance(file_path, Path):
        file_path = str(file_path)

    return _libcaf.save_file_content(root_dir, file_path)

def save_commit(root_dir: str | Path, commit) -> None:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    _libcaf.save_commit(root_dir, commit)

def load_commit(root_dir: str | Path, hash_value) -> Commit:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    commit = _libcaf.load_commit(root_dir, hash_value)

    return commit

def save_tree(root_dir: str | Path, tree: Tree) -> None:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    _libcaf.save_tree(root_dir, tree)

def load_tree(root_dir: str | Path, hash_value) -> Tree:
    if isinstance(root_dir, Path):
        root_dir = str(root_dir)

    tree = _libcaf.load_tree(root_dir, hash_value)

    return tree


__all__ = [
    'hash_file',
    'save_file_content',
    'save_commit',
    'load_commit',
    'save_tree',
    'load_tree',
    'open_content_for_reading',
    'delete_content',
    'Commit',
    'hash_object',
    'Blob',
    'TreeRecord',
    'Tree',
    'TreeRecordType'
]
