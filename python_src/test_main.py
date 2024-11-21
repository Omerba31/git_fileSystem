import os
import pytest
from file_manager import FileManager

# Initialize the FileManager with the path to the shared library
file_manager = FileManager('/workspace/libopenfile.so')


def test_compute_sha1():
    # Create a test file
    test_filename = os.path.join(os.getcwd(), "./files/file2.txt")
    os.makedirs(os.path.dirname(test_filename), exist_ok=True)
    with open(test_filename, 'w') as f:
        f.write("This is a test file for SHA1.")

    # Call the method to compute the SHA1 hash
    hash_output = file_manager.compute_sha1(test_filename)

    # Print the computed hash
    print(f"Computed SHA1 hash: {hash_output}")

    # Check that the hash is not empty
    assert hash_output != "", "Failed to compute SHA1 hash"

def test_open_content():
    # Create a test file
    test_filename = os.path.join(os.getcwd(), "./files/file1.txt")
    test_filename = os.path.join(os.getcwd(), "./files/file1.txt")
    os.makedirs(os.path.dirname(test_filename), exist_ok=True)
    with open(test_filename, 'w') as f:
        f.write("This is a test file.")

    # Compute the SHA1 hash
    hash_output = file_manager.compute_sha1(test_filename)

    # Save the file based on the hash
    root_dir = os.path.join(os.getcwd(), "./objects")
    file_manager.save_file(root_dir, test_filename)

    # Call the method to open the file based on its hash
    fd = file_manager.open_content(root_dir, hash_output)
    assert fd != -1, "Failed to open the file"

    # Try reading the file and comparing the contents to what you intended to write into the file
    with open(test_filename, 'r') as f:
        content = f.read()
    assert content == "This is a test file.", "File content does not match"

    # Try reading the file and comparing the contents to what you intended to write into the file
    with open(test_filename, 'r') as f:
        content = f.read()
    assert content == "This is a test file.", "File content does not match"

    # Clean up
    os.close(fd)

def test_save_file():
    # Create a test file
    test_filename = os.path.join(os.getcwd(), "./files/file3.txt")
    test_filename = os.path.join(os.getcwd(), "./files/file3.txt")
    os.makedirs(os.path.dirname(test_filename), exist_ok=True)
    with open(test_filename, 'w') as f:
        f.write("This is a test file for saving based on hash.")

    # Save the file based on the hash
    root_dir = os.path.join(os.getcwd(), "./objects")
    file_manager.save_file(root_dir, test_filename)

    # Compute the SHA1 hash
    hash_output = file_manager.compute_sha1(test_filename)

    # Check that the file was saved correctly
    saved_file_path = os.path.join(os.getcwd(), f"./objects/{hash_output[:2]}/{hash_output}")
    assert os.path.exists(saved_file_path), "Failed to save the file based on hash"