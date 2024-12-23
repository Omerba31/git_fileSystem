import ctypes
import os

# Add the main project directory to the Python path
import _libcaf


def compute_hash(filename):
    try:
        result, hash_output = _libcaf.compute_hash(filename)
    except UnicodeDecodeError as e:
        raise FileNotFoundError(f"File '{filename}' not found.")

    if result == -1:
        raise FileNotFoundError(f"File '{filename}' not found.")
    if result != 0:
        errno = ctypes.get_errno()
        error_message = f"Failed to compute SHA1 for file '{filename}'. Error code: {errno}, Description: {os.strerror(errno)}"
        raise OSError(errno, error_message)

    return hash_output

def open_content(root_dir, hash_value):
    fd = _libcaf.open_content(root_dir, hash_value)

    if fd == -1:
        raise OSError(f"Failed to open content with hash '{hash_value}' in directory '{root_dir}'")

    return os.fdopen(fd, 'r')

def delete_content(root_dir, hash_value):
    _libcaf.delete_content(root_dir, hash_value)

def save_content(*args):
    """
    Overloaded function for saving content:
    - save_content(root_dir, filename): Save content directly from a file.
    - save_content(root_dir, hash_value, flags): Save content with a hash and custom flags.
    """
    if len(args) == 2:
        root_dir, filename = args
        _libcaf.save_content(root_dir, filename)
    elif len(args) == 3:
        root_dir, hash_value, flags = args
        result, fd, blob_path = _libcaf.save_content(root_dir, hash_value, flags)
        if result != 0:
            raise OSError(f"Failed to save content with hash '{hash_value}' in directory '{root_dir}'")
        return result, fd, blob_path
    else:
        raise TypeError("save_content() takes 2 or 3 arguments")

def save_commit(root_dir, commit):
    result = _libcaf.save_commit(root_dir, commit)
    if result != 0:
        raise OSError(f"Failed to save commit in directory '{root_dir}'")
    return result

def load_commit(root_dir, hash_value):
    result, commit = _libcaf.load_commit(root_dir, hash_value)
    if result != 0:
        raise OSError(f"Failed to load commit with hash '{hash_value}' in directory '{root_dir}'")
    return result, commit


# Import classes and enums
from _libcaf import (
    Commit,
    computeHash,
    Blob,
    TreeRecord,
    Tree,
    TreeRecordType
)

__all__ = [
    'compute_hash',
    'save_content',
    'save_commit',
    'load_commit',
    'open_content',
    'delete_content',
    'Commit',
    'computeHash',
    'Blob',
    'TreeRecord',
    'Tree',
    'TreeRecordType'
]