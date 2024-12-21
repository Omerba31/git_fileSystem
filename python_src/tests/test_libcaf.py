import hashlib
import os
import threading
import time

import libcaf
#TODO:checck with @ido to see if this is the correct import
from _libcaf import compute_hash, Commit, computeHash, Blob, TreeRecord, Tree, TreeRecordType

OBJECTS_DIR = os.path.join(os.getcwd(), "./objects")
INPUT_DIR = "./files"


def create_test_file(dir_path, filename, content):
    full_path = os.path.join(dir_path, filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as file:
        file.write(content)
    return full_path


def test_compute_hash():
    test_filename = "test_compute_hash_test.txt"
    content = "SHA1 computation test: this content will generate a hash"
    test_filepath = create_test_file(INPUT_DIR, test_filename, content)

    # Compute the hash using the file manager
    hash_output = libcaf.compute_hash(test_filepath)

    # Compute the expected hash using hashlib directly
    expected_hash = hashlib.sha1(content.encode('utf-8')).hexdigest()

    # Verify the hash matches the expected result
    assert hash_output == expected_hash, f"Expected hash '{expected_hash}', but got '{hash_output}'"


def test_save_content():
    test_filename = "test_save_content_test.txt"
    content = "Save content test: this content will be saved and verified"
    test_filepath = create_test_file(INPUT_DIR, test_filename, content)

    libcaf.save_content(OBJECTS_DIR, test_filepath)
    hash_output = libcaf.compute_hash(test_filepath)
    saved_file_path = os.path.join(OBJECTS_DIR, f"{hash_output[:2]}/{hash_output}")

    assert os.path.exists(saved_file_path), "Content was not saved correctly"
    with open(saved_file_path, 'r') as saved_file:
        saved_content = saved_file.read()
    assert saved_content == content, "Saved content does not match the original"


def test_open_content():
    test_filename = "test_open_content_test.txt"
    content = "Open content test: this content will be opened and read"
    test_filepath = create_test_file(INPUT_DIR, test_filename, content)

    hash_output = libcaf.compute_hash(test_filepath)
    libcaf.save_content(OBJECTS_DIR, test_filepath)

    with libcaf.open_content(OBJECTS_DIR, hash_output) as file:
        file_content = file.read()
    assert file_content == content, "Content mismatch on open"


def test_save_and_delete_content():
    test_filename = "test_save_and_delete_content_test.txt"
    content = "Save and delete content test: content for save-delete functionality"
    test_filepath = create_test_file(INPUT_DIR, test_filename, content)

    libcaf.save_content(OBJECTS_DIR, test_filepath)
    hash_output = libcaf.compute_hash(test_filepath)
    saved_file_path = os.path.join(OBJECTS_DIR, f"{hash_output[:2]}/{hash_output}")

    assert os.path.exists(saved_file_path), "Content was not saved correctly"
    libcaf.delete_content(OBJECTS_DIR, hash_output)
    assert not os.path.exists(saved_file_path), "Content still exists after deletion"


def test_open_non_existent_file():
    non_existent_hash = "deadbeef" + "0" * 32
    try:
        libcaf.open_content(OBJECTS_DIR, non_existent_hash)
    except OSError as e:
        assert str(e) == f"Failed to open content with hash '{non_existent_hash}' in directory '{OBJECTS_DIR}'"
    else:
        assert False, "Expected OSError was not raised"


def test_compute_hash_non_existent_file():
    non_existent_file = os.path.join(os.getcwd(), "./files/test_compute_hash_non_existent_file.txt")
    try:
        libcaf.compute_hash(non_existent_file)
    except FileNotFoundError as e:
        assert str(e) == f"File '{non_existent_file}' not found."
    else:
        assert False, "Expected FileNotFoundError was not raised"


def test_delete_non_existent_file():
    non_existent_hash = "deadbeef" + "0" * 32
    try:
        libcaf.delete_content(OBJECTS_DIR, non_existent_hash)
    except Exception as e:
        assert False, f"Deleting a non-existent content raised an exception: {e}"
    else:
        assert True, "Deleting a non-existent content should silently succeed"


def test_save_large_file():
    test_filename = "test_save_large_file_test.txt"
    content = "Large file test: " + "A" * (10 ** 6)  # 1 MB of 'A'
    test_filepath = create_test_file(INPUT_DIR, test_filename, content)

    libcaf.save_content(OBJECTS_DIR, test_filepath)
    hash_output = libcaf.compute_hash(test_filepath)
    saved_file_path = os.path.join(OBJECTS_DIR, f"{hash_output[:2]}/{hash_output}")

    assert os.path.exists(saved_file_path), "Failed to save the large content"
    with open(saved_file_path, 'r') as saved_file:
        saved_content = saved_file.read()
    assert saved_content == content, "Saved large content does not match the original"


def test_concurrent_read_and_write():
    test_filename = "test_concurrent_read_and_write_test.txt"
    content = "Concurrent read and write test: This content will be accessed by multiple threads."
    test_filepath = create_test_file(INPUT_DIR, test_filename, content)

    def save_content():
        libcaf.save_content(OBJECTS_DIR, test_filepath)

    def read_content():
        hash_output = libcaf.compute_hash(test_filepath)
        with libcaf.open_content(OBJECTS_DIR, hash_output) as file:
            file_content = file.read()
            assert file_content == content, "File content mismatch during concurrent read"

    save_thread = threading.Thread(target=save_content)
    read_thread = threading.Thread(target=read_content)

    save_thread.start()
    time.sleep(0.1)
    read_thread.start()

    save_thread.join()
    read_thread.join()


def test_concurrent_writes():
    test_filename = "test_concurrent_writes_test.txt"
    content = "Concurrent writes test: content to simulate multiple saves"
    test_filepath = create_test_file(INPUT_DIR, test_filename, content)

    def save_content():
        libcaf.save_content(OBJECTS_DIR, test_filepath)

    threads = [threading.Thread(target=save_content) for _ in range(5)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    hash_output = libcaf.compute_hash(test_filepath)
    saved_file_path = os.path.join(OBJECTS_DIR, f"{hash_output[:2]}/{hash_output}")
    assert os.path.exists(saved_file_path), "File should exist after concurrent writes"


def test_concurrent_delete():
    test_filename = "test_concurrent_delete_test.txt"
    content = "Concurrent delete test: content for delete contention"
    test_filepath = create_test_file(INPUT_DIR, test_filename, content)

    hash_output = libcaf.compute_hash(test_filepath)

    def save_content():
        libcaf.save_content(OBJECTS_DIR, test_filepath)

    def delete_locked_file():
        time.sleep(0.2)
        libcaf.delete_content(OBJECTS_DIR, hash_output)

    save_thread = threading.Thread(target=save_content)
    delete_thread = threading.Thread(target=delete_locked_file)

    save_thread.start()
    delete_thread.start()

    save_thread.join()
    delete_thread.join()

    saved_file_path = os.path.join(OBJECTS_DIR, f"{hash_output[:2]}/{hash_output}")
    assert not os.path.exists(saved_file_path), "File still exists after delete operation"


def test_multi_file_lock_contention():
    test_filename1 = "test_multi_lock_contention_1.txt"
    test_filename2 = "test_multi_lock_contention_2.txt"
    content1 = "Content for multi-lock test file 1"
    content2 = "Content for multi-lock test file 2"

    test_filepath1 = create_test_file(INPUT_DIR, test_filename1, content1)
    test_filepath2 = create_test_file(INPUT_DIR, test_filename2, content2)

    def save_content(filepath):
        libcaf.save_content(OBJECTS_DIR, filepath)

    thread1 = threading.Thread(target=save_content, args=(test_filepath1,))
    thread2 = threading.Thread(target=save_content, args=(test_filepath2,))

    thread1.start()
    time.sleep(0.1)
    thread2.start()

    thread1.join()
    thread2.join()

    hash1 = libcaf.compute_hash(test_filepath1)
    hash2 = libcaf.compute_hash(test_filepath2)
    saved_file_path1 = os.path.join(OBJECTS_DIR, f"{hash1[:2]}/{hash1}")
    saved_file_path2 = os.path.join(OBJECTS_DIR, f"{hash2[:2]}/{hash2}")

    assert os.path.exists(saved_file_path1), "File 1 not saved correctly"
    assert os.path.exists(saved_file_path2), "File 2 not saved correctly"



# hashTypes tests

def test_computeHash_commit():
    # Create a Commit object
    commit = Commit("1234567890abcdef", "Author", "Initial commit", 1234567890)

    # Compute the hash
    hash_output = computeHash(commit)

    # Verify the hash is not an error code
    assert hash_output is not None, "Failed to compute hash for Commit"
    assert len(hash_output) == 40, f"Hash length is not as expected: {len(hash_output)}"

def test_computeHash_tree():
    # Create TreeRecord objects
    record1 = TreeRecord(TreeRecordType.TREE, "1234567890abcdef", "record1")
    record2 = TreeRecord(TreeRecordType.BLOB, "abcdef1234567890", "record2")

    # Create a Tree object
    tree = Tree({"record1": record1, "record2": record2})

    # Compute the hash
    hash_output = computeHash(tree)

    # Verify the hash is not an error code
    assert hash_output is not None, "Failed to compute hash for Tree"
    assert len(hash_output) == 40, f"Hash length is not as expected: {len(hash_output)}"

def test_same_blob_objects_get_same_hash():
    # Create two identical Blob objects
    blob1 = Blob("1234567890abcdef")
    blob2 = Blob("1234567890abcdef")

    # Compute the hash for both objects
    hash_output1 = computeHash(blob1)
    hash_output2 = computeHash(blob2)

    # Verify the hashes are the same
    assert hash_output1 == hash_output2, "Hashes for identical Blob objects do not match"

def test_same_commit_objects_get_same_hash():
    # Create two identical Commit objects
    commit1 = Commit("1234567890abcdef", "Author", "Initial commit", 1234567890)
    commit2 = Commit("1234567890abcdef", "Author", "Initial commit", 1234567890)

    # Compute the hash for both objects
    hash_output1 = computeHash(commit1)
    hash_output2 = computeHash(commit2)

    # Verify the hashes are the same
    assert hash_output1 == hash_output2, "Hashes for identical Commit objects do not match"


def test_same_tree_objects_get_same_hash():
    # Create TreeRecord objects
    record1 = TreeRecord(TreeRecordType.TREE, "1234567890abcdef", "record1")
    record2 = TreeRecord(TreeRecordType.BLOB, "abcdef1234567890", "record2")

    # Create two identical Tree objects
    tree1 = Tree({"record1": record1, "record2": record2})
    tree2 = Tree({"record1": record1, "record2": record2})

    # Compute the hash for both objects
    hash_output1 = computeHash(tree1)
    hash_output2 = computeHash(tree2)

    # Verify the hashes are the same
    assert hash_output1 == hash_output2, "Hashes for identical Tree objects do not match"



def test_different_hashes_for_different_blobs():
    # Create two different Blob objects
    blob1 = Blob("1234567890abcdef")
    blob2 = Blob("abcdef1234567890")

    # Compute the hash for both objects
    hash_output1 = computeHash(blob1)
    hash_output2 = computeHash(blob2)

    # Verify the hashes are different
    assert hash_output1 != hash_output2, "Hashes for different Blob objects are the same"

def test_different_hashes_for_different_trees():
    # Create TreeRecord objects
    record1 = TreeRecord(TreeRecordType.TREE, "1234567890abcdef", "record1")
    record2 = TreeRecord(TreeRecordType.BLOB, "abcdef1234567890", "record2")
    record3 = TreeRecord(TreeRecordType.TREE, "fedcba0987654321", "record3")

    # Create two different Tree objects
    tree1 = Tree({"record1": record1, "record2": record2})
    tree2 = Tree({"record1": record1, "record2": record3})

    # Compute the hash for both objects
    hash_output1 = computeHash(tree1)
    hash_output2 = computeHash(tree2)

    # Verify the hashes are different
    assert hash_output1 != hash_output2, "Hashes for different Tree objects are the same"

def test_different_hashes_for_different_commits():
    # Create two different Commit objects
    commit1 = Commit("1234567890abcdef", "Author1", "Initial commit", 1234567890)
    commit2 = Commit("abcdef1234567890", "Author2", "Second commit", 1234567891)

    # Compute the hash for both objects
    hash_output1 = computeHash(commit1)
    hash_output2 = computeHash(commit2)

    # Verify the hashes are different
    assert hash_output1 != hash_output2, "Hashes for different Commit objects are the same"