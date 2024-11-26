import os
import ctypes
import pytest
from unittest.mock import patch
from file_manager import FileManager
import threading
from threading import Thread, Event
import time

OBJECTS_DIR = os.path.join(os.getcwd(), "./objects")
INPUT_DIR = "./files"
file_manager = FileManager('/workspace/libcaf.so')


def test_compute_sha1():
    test_filename = "test_compute_sha1_test.txt"
    content = "SHA1 computation test: this content will generate a hash"
    test_filepath = file_manager.create_test_file(INPUT_DIR, test_filename, content)

    hash_output = file_manager.compute_sha1(test_filepath)
    assert hash_output != "", "Failed to compute SHA1 hash"

def test_save_file():
    test_filename = "test_save_file_test.txt"
    content = "Save file test: this content will be saved and verified"
    test_filepath = file_manager.create_test_file(INPUT_DIR, test_filename, content)

    file_manager.save_file(OBJECTS_DIR, test_filepath)
    hash_output = file_manager.compute_sha1(test_filepath)
    saved_file_path = os.path.join(OBJECTS_DIR, f"{hash_output[:2]}/{hash_output}")

    assert os.path.exists(saved_file_path), "File was not saved correctly"
    with open(saved_file_path, 'r') as saved_file:
        saved_content = saved_file.read()
    assert saved_content == content, "Saved file content does not match the original"

def test_open_file():
    test_filename = "test_open_file_test.txt"
    content = "Open file test: this content will be opened and read"
    test_filepath = file_manager.create_test_file(INPUT_DIR, test_filename, content)

    hash_output = file_manager.compute_sha1(test_filepath)
    file_manager.save_file(OBJECTS_DIR, test_filepath)
    fd = file_manager.open_file(OBJECTS_DIR, hash_output)

    assert fd != -1, "Failed to open the file"
    with os.fdopen(fd, 'r') as file:
        file_content = file.read()
    assert file_content == content, "File content mismatch on open"

def test_save_and_delete_file():
    test_filename = "test_save_and_delete_file_test.txt"
    content = "Save and delete file test: content for save-delete functionality"
    test_filepath = file_manager.create_test_file(INPUT_DIR, test_filename, content)

    file_manager.save_file(OBJECTS_DIR, test_filepath)
    hash_output = file_manager.compute_sha1(test_filepath)
    saved_file_path = os.path.join(OBJECTS_DIR, f"{hash_output[:2]}/{hash_output}")

    assert os.path.exists(saved_file_path), "File was not saved correctly"
    file_manager.delete_file(OBJECTS_DIR, hash_output)
    assert not os.path.exists(saved_file_path), "File still exists after deletion"

def test_save_same_file_twice():
    test_filename = "test_save_same_file_twice_test.txt"
    content = "Save same file twice test: content to check overwrite behavior"
    test_filepath = file_manager.create_test_file(INPUT_DIR, test_filename, content)

    file_manager.save_file(OBJECTS_DIR, test_filepath)
    hash_output = file_manager.compute_sha1(test_filepath)
    file_manager.save_file(OBJECTS_DIR, test_filepath)

    saved_file_path = os.path.join(OBJECTS_DIR, f"{hash_output[:2]}/{hash_output}")
    assert os.path.exists(saved_file_path), "File does not exist after saving twice"
    with open(saved_file_path, 'r') as f:
        file_content = f.read()
    assert file_content == content, "File content mismatch after saving twice"

def test_save_and_delete_file():
    test_filename = "test_save_and_delete_file_test.txt"
    content = "Save and delete file test: content for save-delete functionality"
    test_filepath = file_manager.create_test_file(INPUT_DIR, test_filename, content)

    file_manager.save_file(OBJECTS_DIR, test_filepath)
    hash_output = file_manager.compute_sha1(test_filepath)
    saved_file_path = os.path.join(OBJECTS_DIR, f"{hash_output[:2]}/{hash_output}")

    assert os.path.exists(saved_file_path), "File was not saved correctly"
    file_manager.delete_file(OBJECTS_DIR, hash_output)
    assert not os.path.exists(saved_file_path), "File still exists after deletion"

def test_open_non_existent_file():
    non_existent_hash = "deadbeef" + "0" * 32
    try:
        file_manager.open_file(OBJECTS_DIR, non_existent_hash)
    except OSError as e:
        assert str(e) == f"Failed to open file with hash '{non_existent_hash}' in directory '{OBJECTS_DIR}'"
    else:
        assert False, "Expected OSError was not raised"

def test_compute_hash_non_existent_file():
    non_existent_file = os.path.join(os.getcwd(), "./files/test_compute_hash_non_existent_file.txt")
    try:
        file_manager.compute_sha1(non_existent_file)
    except FileNotFoundError as e:
        assert str(e) == f"File '{non_existent_file}' not found."
    else:
        assert False, "Expected FileNotFoundError was not raised"

def test_delete_non_existent_file():
    non_existent_hash = "deadbeef" + "0" * 32 
    
    try:
        file_manager.delete_file(OBJECTS_DIR, non_existent_hash)
    except Exception as e:
        assert False, f"Deleting a non-existent file raised an exception: {e}"
    else:
        assert True, "Deleting a non-existent file should silently succeed"

def test_save_large_file():
    test_filename = "test_save_large_file_test.txt"
    content = "Large file test: " + "A" * (10**6)  # 1 MB of 'A'
    test_filepath = file_manager.create_test_file(INPUT_DIR, test_filename, content)

    file_manager.save_file(OBJECTS_DIR, test_filepath)
    hash_output = file_manager.compute_sha1(test_filepath)
    saved_file_path = os.path.join(OBJECTS_DIR, f"{hash_output[:2]}/{hash_output}")

    assert os.path.exists(saved_file_path), "Failed to save the large file"
    with open(saved_file_path, 'r') as saved_file:
        saved_content = saved_file.read()
    assert saved_content == content, "Saved large file content does not match the original"

def test_concurrent_read_and_write():
    test_filename = "test_concurrent_read_and_write_test.txt"
    content = "Concurrent read and write test: This content will be accessed by multiple threads."
    test_filepath = file_manager.create_test_file(INPUT_DIR, test_filename, content)

    def save_file():
        file_manager.save_file(OBJECTS_DIR, test_filepath)

    def read_file():
        hash_output = file_manager.compute_sha1(test_filepath)
        fd = file_manager.open_file(OBJECTS_DIR, hash_output)
        if fd >= 0:
            with os.fdopen(fd, 'r') as file:
                file_content = file.read()
            assert file_content == content, "File content mismatch during concurrent read"
        else:
            assert False, "Failed to open file during concurrent write"

    save_thread = threading.Thread(target=save_file)
    read_thread = threading.Thread(target=read_file)

    save_thread.start()
    time.sleep(0.1)
    read_thread.start()

    save_thread.join()
    read_thread.join()

def test_lock_blocking():
    test_filename = "test_lock_blocking_test.txt"
    content = "Lock blocking test: content to simulate lock contention"
    test_filepath = file_manager.create_test_file(INPUT_DIR, test_filename, content)

    hash_output = file_manager.compute_sha1(test_filepath)
    save_done = threading.Event()

    def save_file():
        try:
            fd = file_manager.open_file(OBJECTS_DIR, hash_output)
            assert fd != -1, "Failed to open file in save_file"
            save_done.set()
            time.sleep(3)
            os.close(fd)
        except Exception as e:
            save_done.set()  # Ensure the event is set even if an error occurs
            raise e

    def open_locked_file():
        assert save_done.wait(timeout=5), "Timeout waiting for save_file to lock the file."
        fd = file_manager.open_file(OBJECTS_DIR, hash_output)
        assert fd == -1, "File should not open while locked"

    save_thread = threading.Thread(target=save_file)
    lock_thread = threading.Thread(target=open_locked_file)

    save_thread.start()
    lock_thread.start()

    save_thread.join()
    lock_thread.join()

    def save_file():
        print("save_file started.")
        try:
            fd = file_manager.open_file(OBJECTS_DIR, hash_output)
            assert fd != -1, "Failed to open file in save_file"
            print(f"save_file: acquired lock with fd={fd}.")
            save_done.set()  # Signal that the file is locked
            time.sleep(3)  # Hold the lock for longer to ensure overlap
            os.close(fd)  # Release the lock
            print("save_file: released lock.")
        except Exception as e:
            print(f"save_file error: {e}")
            save_done.set()

    def open_locked_file():
        print("open_locked_file: Waiting for save_file to signal lock.")
        if not save_done.wait(timeout=5):
            raise TimeoutError("Timeout waiting for save_file to lock the file.")
        print("open_locked_file: Attempting to open locked file.")
        fd = file_manager.open_file(OBJECTS_DIR, hash_output)
        print(f"open_locked_file: open_content returned fd={fd}.")
        assert fd == -1, "Read should fail when file is locked for writing"

    save_thread = threading.Thread(target=save_file)
    lock_thread = threading.Thread(target=open_locked_file)

    save_thread.start()
    lock_thread.start()

    save_thread.join()
    lock_thread.join()

def test_concurrent_writes():
    test_filename = "test_concurrent_writes_test.txt"
    content = "Concurrent writes test: content to simulate multiple saves"
    test_filepath = file_manager.create_test_file(INPUT_DIR, test_filename, content)

    def save_file():
        file_manager.save_file(OBJECTS_DIR, test_filepath)

    threads = [threading.Thread(target=save_file) for _ in range(5)]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    hash_output = file_manager.compute_sha1(test_filepath)
    saved_file_path = os.path.join(OBJECTS_DIR, f"{hash_output[:2]}/{hash_output}")
    assert os.path.exists(saved_file_path), "File should exist after concurrent writes"

def test_concurrent_delete():
    test_filename = "test_concurrent_delete_test.txt"
    content = "Concurrent delete test: content for delete contention"
    test_filepath = file_manager.create_test_file(INPUT_DIR, test_filename, content)

    hash_output = file_manager.compute_sha1(test_filepath)

    def save_file():
        file_manager.save_file(OBJECTS_DIR, test_filepath)

    def delete_locked_file():
        time.sleep(0.2)
        file_manager.delete_file(OBJECTS_DIR, hash_output)

    save_thread = threading.Thread(target=save_file)
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

    test_filepath1 = file_manager.create_test_file(INPUT_DIR, test_filename1, content1)
    test_filepath2 = file_manager.create_test_file(INPUT_DIR, test_filename2, content2)

    def save_file(filepath):
        file_manager.save_file(OBJECTS_DIR, filepath)

    thread1 = threading.Thread(target=save_file, args=(test_filepath1,))
    thread2 = threading.Thread(target=save_file, args=(test_filepath2,))

    thread1.start()
    time.sleep(0.1)
    thread2.start()

    thread1.join()
    thread2.join()

    hash1 = file_manager.compute_sha1(test_filepath1)
    hash2 = file_manager.compute_sha1(test_filepath2)
    saved_file_path1 = os.path.join(OBJECTS_DIR, f"{hash1[:2]}/{hash1}")
    saved_file_path2 = os.path.join(OBJECTS_DIR, f"{hash2[:2]}/{hash2}")

    assert os.path.exists(saved_file_path1), "File 1 not saved correctly"
    assert os.path.exists(saved_file_path2), "File 2 not saved correctly"

def test_lock_with_timeout():
    test_filename = "test_lock_with_timeout_test.txt"
    content = "Lock with timeout test: simulates file lock timeout"
    test_filepath = file_manager.create_test_file(INPUT_DIR, test_filename, content)

    hash_output = file_manager.compute_sha1(test_filepath)
    lock_acquired_event = threading.Event()

    def lock_file():
        try:
            fd = file_manager.open_file(OBJECTS_DIR, hash_output)
            assert fd != -1, "Failed to acquire lock"
            lock_acquired_event.set()
            time.sleep(5)
            os.close(fd)
        except Exception as e:
            lock_acquired_event.set()  # Ensure the event is set even if an error occurs
            raise e

    def try_lock_with_timeout():
        assert lock_acquired_event.wait(timeout=1), "Lock was not acquired in time"
        start_time = time.time()
        fd = file_manager.open_file(OBJECTS_DIR, hash_output)
        elapsed_time = time.time() - start_time
        assert fd == -1, "Lock should timeout"
        assert elapsed_time >= 1, f"Timeout duration not respected: {elapsed_time}s"

    lock_thread = threading.Thread(target=lock_file)
    timeout_thread = threading.Thread(target=try_lock_with_timeout)

    lock_thread.start()
    timeout_thread.start()

    lock_thread.join()
    timeout_thread.join()
    test_filename = "test_lock_with_timeout_test.txt"
    content = "Lock with timeout test: simulates file lock timeout"
    test_filepath = file_manager.create_test_file(INPUT_DIR, test_filename, content)

    hash_output = file_manager.compute_sha1(test_filepath)
    lock_acquired_event = threading.Event()

    def lock_file():
        fd = file_manager.open_file(OBJECTS_DIR, hash_output)
        assert fd != -1, "Failed to acquire lock"
        lock_acquired_event.set()
        time.sleep(5)
        os.close(fd)

    def try_lock_with_timeout():
        assert lock_acquired_event.wait(timeout=1), "Lock was not acquired in time"
        start_time = time.time()
        fd = file_manager.open_file(OBJECTS_DIR, hash_output)
        elapsed_time = time.time() - start_time
        assert fd == -1, "Lock should timeout"
        assert elapsed_time >= 1, f"Timeout duration not respected: {elapsed_time}s"

    lock_thread = threading.Thread(target=lock_file)
    timeout_thread = threading.Thread(target=try_lock_with_timeout)

    lock_thread.start()
    timeout_thread.start()

    lock_thread.join()
    timeout_thread.join()