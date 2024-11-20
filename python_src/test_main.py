import os
import ctypes
import pytest

# Load the shared library
lib = ctypes.CDLL('/workspace/libopenfile.so')

# Define the argument and return types for the C functions
lib.open_content.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
lib.open_content.restype = ctypes.c_int

lib.compute_sha1.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
lib.compute_sha1.restype = None

lib.save_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
lib.save_file.restype = None

def python_compute_sha1(filename):
    hash_output = ctypes.create_string_buffer(41)  # SHA1 hash is 40 characters + null terminator
    lib.compute_sha1(filename.encode('utf-8'), hash_output)
    return hash_output.value.decode('utf-8')


def test_compute_sha1():
    # Create a test file
    test_filename = os.path.join(os.getcwd(), "./files/file2.txt")
    os.makedirs(os.path.dirname(test_filename), exist_ok=True)
    with open(test_filename, 'w') as f:
        f.write("This is a test file for SHA1.")

    # Prepare a buffer to receive the SHA1 hash
    hash_output = ctypes.create_string_buffer(41)  # SHA1 hash is 40 characters + null terminator

    # Call the C function
    lib.compute_sha1(test_filename.encode('utf-8'), hash_output)

    # Print the computed hash
    print(f"Computed SHA1 hash: {hash_output.value.decode('utf-8')}")

    # Check that the hash is not empty
    assert hash_output.value.decode('utf-8') != "", "Failed to compute SHA1 hash"

def test_open_content():
    # Create a test file
    test_filename = os.path.join(os.getcwd(), "./files/file1.txt")
    os.makedirs(os.path.dirname(test_filename), exist_ok=True)
    with open(test_filename, 'w') as f:
        f.write("This is a test file.")

    # Compute the SHA1 hash
    hash_output = ctypes.create_string_buffer(41)  # SHA1 hash is 40 characters + null terminator
    lib.compute_sha1(test_filename.encode('utf-8'), hash_output)

    # Save the file based on the hash
    root_dir = os.path.join(os.getcwd(), "./objects")
    lib.save_file(root_dir.encode('utf-8'), test_filename.encode('utf-8'))

    # Call the C function to open the file based on its hash
    fd = lib.open_content(root_dir.encode('utf-8'), hash_output.value)
    assert fd != -1, "Failed to open the file"

    # Try reading the file and comparing the contents to what you intended to write into the file
    with open(test_filename, 'r') as f:
        content = f.read()
    assert content == "This is a test file.", "File content does not match"

    # Clean up
    os.close(fd)


def test_save_file():
    # Create a test file
    test_filename = os.path.join(os.getcwd(), "./files/file3.txt")
    os.makedirs(os.path.dirname(test_filename), exist_ok=True)
    with open(test_filename, 'w') as f:
        f.write("This is a test file for saving based on hash.")

    # Save the file based on the hash
    root_dir = os.path.join(os.getcwd(), "./objects")
    lib.save_file(root_dir.encode('utf-8'), test_filename.encode('utf-8'))

    # Compute the SHA1 hash
    hash_output = ctypes.create_string_buffer(41)  # SHA1 hash is 40 characters + null terminator
    lib.compute_sha1(test_filename.encode('utf-8'), hash_output)

    # Check that the file was saved correctly
    saved_file_path = os.path.join(os.getcwd(), f"./objects/{hash_output.value.decode('utf-8')[:2]}/{hash_output.value.decode('utf-8')}")
    assert os.path.exists(saved_file_path), "Failed to save the file based on hash"

