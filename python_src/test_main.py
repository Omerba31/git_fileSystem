import os
import ctypes
import pytest

# Load the shared library
lib = ctypes.CDLL('/workspace/libopenfile.so')



lib.compute_sha1.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
lib.compute_sha1.restype = None

lib.save_file_based_on_hash.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
lib.save_file_based_on_hash.restype = None

# Define the argument and return types for the C functions
lib.open_file_by_hash.argtypes = [ctypes.c_char_p]
lib.open_file_by_hash.restype = ctypes.c_int

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

def test_open_file_by_hash():
    # Create a test file
    test_filename = os.path.join(os.getcwd(), "./files/file2.txt")
    os.makedirs(os.path.dirname(test_filename), exist_ok=True)
    with open(test_filename, 'w') as f:
        f.write("This is a test file for SHA1.")

    # Call the C function
    fd = lib.open_file_by_hash(test_filename.encode('utf-8'))
    assert fd != -1, "Failed to open the file"

    # Clean up
    os.close(fd)

def test_save_file_based_on_hash():
    # Create a test file
    test_filename = os.path.join(os.getcwd(), "./files/file2.txt")
    os.makedirs(os.path.dirname(test_filename), exist_ok=True)
    with open(test_filename, 'w') as f:
        f.write("This is a test file for SHA1.")

    # Prepare a buffer to receive the SHA1 hash
    hash_output = ctypes.create_string_buffer(41)  # SHA1 hash is 40 characters + null terminator

    # Compute the SHA1 hash
    lib.compute_sha1(test_filename.encode('utf-8'), hash_output)

    # Save the file based on the hash
    lib.save_file_based_on_hash(test_filename.encode('utf-8'), hash_output)

    # Check that the file was saved correctly
    saved_file_path = os.path.join(os.getcwd(), f"./hashed_files/{hash_output.value.decode('utf-8')[:2]}/{hash_output.value.decode('utf-8')}")
    assert os.path.exists(saved_file_path), "Failed to save the file based on hash"

