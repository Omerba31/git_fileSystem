import ctypes
import os

import _libcaf
from _libcaf import Commit


def compute_sha1(filename):
    result, hash_output = _libcaf.compute_sha1(filename)

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


all = ['compute_sha1',
       'save_content',
       'open_content',
       'delete_content',
       'Commit']
