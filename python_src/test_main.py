import os
import pytest
from main import open_file_by_hash

def test_open_file_by_hash():
    # Create a test file
    test_filename = os.path.join(os.getcwd(), "./files/file1.txt")
    os.makedirs(os.path.dirname(test_filename), exist_ok=True)
    with open(test_filename, 'w') as f:
        f.write("This is a test file.")

    # Test the function
    fd = open_file_by_hash(test_filename)
    assert fd != -1, "Failed to open the file"

    # Clean up
    os.close(fd)

def test_failure():
    # This test is designed to fail
    assert 1 == 2, "This test is designed to fail"