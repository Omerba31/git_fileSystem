import threading
import time

from pytest import mark, raises

from libcaf import hash_file, delete_content, open_content_for_reading_fd, save_file_content


class TestRepo:
    def test_open_non_existent_file(self, temp_repo):
        non_existent_hash = "deadbeef" + "0" * 32

        with raises(OSError):
            open_content_for_reading_fd(temp_repo, non_existent_hash)

    def test_delete_non_existent_file(self, temp_repo):
        non_existent_hash = "deadbeef" + "0" * 32
        delete_content(temp_repo, non_existent_hash)

    @mark.parametrize("temp_content_length", [1, 10, 100, 1000, 10000, 100000, 1000000])
    def test_multi_file_lock_contention(self, temp_repo, temp_content_file_factory):
        temp_content_file1, _ = temp_content_file_factory()
        temp_content_file2, _ = temp_content_file_factory()

        def save(filepath):
            save_file_content(temp_repo, filepath)

        thread1 = threading.Thread(target=save, args=(temp_content_file1,))
        thread2 = threading.Thread(target=save, args=(temp_content_file2,))

        thread1.start()
        time.sleep(0.1)
        thread2.start()

        thread1.join()
        thread2.join()

        hash1 = hash_file(temp_content_file1)
        hash2 = hash_file(temp_content_file2)
        saved_file_path1 = temp_repo / f"{hash1[:2]}/{hash1}"
        saved_file_path2 = temp_repo / f"{hash2[:2]}/{hash2}"

        assert saved_file_path1.exists()
        assert saved_file_path2.exists()
