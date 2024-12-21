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

def save_content(root_dir, filename):
    _libcaf.save_content(root_dir, filename)

def open_content(root_dir, hash_value):
    fd = _libcaf.open_content(root_dir, hash_value)

    if fd == -1:
        raise OSError(f"Failed to open content with hash '{hash_value}' in directory '{root_dir}'")

    return os.fdopen(fd, 'r')

def delete_content(root_dir, hash_value):
    _libcaf.delete_content(root_dir, hash_value)

__all__ = [
    'compute_hash',
    'save_content',
    'open_content',
    'delete_content',
    'Commit',
    'computeHash',
    'Blob',
    'TreeRecord',
    'Tree',
    'TreeRecordType'
]