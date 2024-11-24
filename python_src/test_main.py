import os
import pytest
from unittest.mock import patch
from file_manager import FileManager

# Mimic #define in Python by using a constant
OBJECTS_DIR = os.path.join(os.getcwd(), "./objects")

# Initialize the FileManager with the path to the shared library
file_manager = FileManager('/workspace/libcaf.so')

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
    os.makedirs(os.path.dirname(test_filename), exist_ok=True)
    with open(test_filename, 'w') as f:
        f.write("This is a test file.")

    # Compute the SHA1 hash
    hash_output = file_manager.compute_sha1(test_filename)

    # Save the file based on the hash
    file_manager.save_file(OBJECTS_DIR, test_filename)

    # Call the method to open the file based on its hash
    fd = file_manager.open_content(OBJECTS_DIR, hash_output)
    assert fd != -1, "Failed to open the file"

    # Try reading the file and comparing the contents to what you intended to write into the file
    with os.fdopen(fd, 'r') as f:
        # Read and compare the contents
        content = f.read()
    assert content == "This is a test file.", "File content does not match"

    # Clean up (file descriptor is automatically closed by the 'with' statement)

def test_save_file():
    # Create a test file
    test_filename = os.path.join(os.getcwd(), "./files/file3.txt")
    os.makedirs(os.path.dirname(test_filename), exist_ok=True)
    original_content = "This is a test file for saving based on hash."
    with open(test_filename, 'w') as f:
        f.write(original_content)

    # Save the file based on the hash
    file_manager.save_file(OBJECTS_DIR, test_filename)

    # Compute the SHA1 hash
    hash_output = file_manager.compute_sha1(test_filename)

    # Construct the path of the saved file
    saved_file_path = os.path.join(OBJECTS_DIR, f"{hash_output[:2]}/{hash_output}")

    # Check that the file was saved correctly
    assert os.path.exists(saved_file_path), "Failed to save the file based on hash"

    # Read the content of the saved file and verify it matches the original content
    with open(saved_file_path, 'r') as saved_file:
        saved_content = saved_file.read()
    assert saved_content == original_content, "Saved file content does not match the original"

    print("Test passed: File saved and content verified successfully.")

def test_save_same_file_twice():
    test_filename = os.path.join(os.getcwd(), "./files/file4.txt")
    os.makedirs(os.path.dirname(test_filename), exist_ok=True)
    with open(test_filename, 'w') as f:
        f.write("This is a test file for duplication check.")

    # Save the file based on the hash
    file_manager.save_file(OBJECTS_DIR, test_filename)
    
    # Compute the hash of the file
    hash_output = file_manager.compute_sha1(test_filename)

    # Save the same file again
    file_manager.save_file(OBJECTS_DIR, test_filename)

    # Check that the file still exists and is not corrupted
    saved_file_path = os.path.join(OBJECTS_DIR, f"{hash_output[:2]}/{hash_output}")
    assert os.path.exists(saved_file_path), "File does not exist after saving twice"
    
    # Verify the content of the saved file
    with open(saved_file_path, 'r') as f:
        content = f.read()
    assert content == "This is a test file for duplication check.", "File content corrupted after saving twice"

def test_save_file_same_content_different_name():
    content = "This is a test file for identical content."

    # Create two files with the same content but different names
    test_filename1 = os.path.join(os.getcwd(), "./files/file5.txt")
    test_filename2 = os.path.join(os.getcwd(), "./files/file6.txt")
    os.makedirs(os.path.dirname(test_filename1), exist_ok=True)
    with open(test_filename1, 'w') as f1, open(test_filename2, 'w') as f2:
        f1.write(content)
        f2.write(content)

    # Compute their hashes
    hash1 = file_manager.compute_sha1(test_filename1)
    hash2 = file_manager.compute_sha1(test_filename2)

    # Verify the hashes are different since the filenames are different
    assert hash1 != hash2, "Hashes for files with different names should be different"
    print(f"Hash1: {hash1}, Hash2: {hash2}")

    file_manager.save_file(OBJECTS_DIR, test_filename1)
    file_manager.save_file(OBJECTS_DIR, test_filename2)

    saved_file_path1 = os.path.join(OBJECTS_DIR, f"{hash1[:2]}/{hash1}")
    saved_file_path2 = os.path.join(OBJECTS_DIR, f"{hash2[:2]}/{hash2}")

    # Ensure both files are saved in their respective locations
    assert os.path.exists(saved_file_path1), f"File {saved_file_path1} does not exist in the database1"
    assert os.path.exists(saved_file_path2), f"File {saved_file_path2} does not exist in the database2"

def test_save_and_delete_file():
    test_filename = os.path.join(os.getcwd(), "./files/file7.txt")
    os.makedirs(os.path.dirname(test_filename), exist_ok=True)
    with open(test_filename, 'w') as f:
        f.write("This is a test file for save and delete.")

    # Save the file
    file_manager.save_file(OBJECTS_DIR, test_filename)

    # Compute the hash
    hash_output = file_manager.compute_sha1(test_filename)

    # Confirm the file exists before deletion (➕)
    saved_file_path = os.path.join(OBJECTS_DIR, f"{hash_output[:2]}/{hash_output}")  # Existed code, used for pre-check (✅)
    assert os.path.exists(saved_file_path), "File was not saved correctly"  # Added check for existence before deletion (➕)
        
    # Remove the file
    file_manager.delete_file_based_on_hash(OBJECTS_DIR, hash_output)

    # Check that the file no longer exists
    assert not os.path.exists(saved_file_path), "File still exists after deletion"

def test_open_non_existent_file():
    # Generate a random hash that doesn't exist
    non_existent_hash = "deadbeef" + "0" * 32  # Random SHA1-like hash
    
    # Attempt to open the non-existent file
    fd = file_manager.open_content(OBJECTS_DIR, non_existent_hash)
    
    # Verify that the function returns -1 or an equivalent error code
    assert fd == -1, "Opening a non-existent file should fail"

def test_compute_hash_non_existent_file():
    non_existent_file = os.path.join(os.getcwd(), "./files/non_existent_file.txt")
    print(f"Non-existent file path: {non_existent_file}")

    # Call compute_sha1 and expect it to return an empty string (➕)
    hash_output = file_manager.compute_sha1(non_existent_file)

    # Assert that the output is an empty string for a non-existent file (➕)
    assert hash_output == "", "Expected empty hash output for non-existent file"  # Adjusted expectation (➕)

def test_delete_non_existent_file():
    non_existent_hash = "deadbeef" + "0" * 32  # Random SHA1-like hash
    
    # Attempt to delete a non-existent file
    try:
        file_manager.delete_file_based_on_hash(OBJECTS_DIR, non_existent_hash)
    except Exception as e:
        assert False, f"Deleting a non-existent file raised an exception: {e}"
    else:
        assert True, "Deleting a non-existent file should silently succeed"






