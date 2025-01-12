import hashlib
import threading
import time
from libcaf import hash_file, delete_content, open_content_for_reading_fd, save_file_content
from pytest import mark


@mark.parametrize("temp_content_length", [1]) # 0, 1, 10, 100, 1000, 10000, 100000, 1000000
class TestContent:
    def test_hash_file(self, temp_content):
        file, content = temp_content

        actual = hash_file(file)
        expected = hashlib.sha1(content.encode('utf-8')).hexdigest()

        assert actual == expected

    def test_save_file_content(self, temp_repo, temp_content):
        file, expected_content = temp_content

        save_file_content(temp_repo, file)
        file_hash = hash_file(file)

        saved_file = temp_repo / f"{file_hash[:2]}/{file_hash}"
        assert saved_file.exists()

        saved_content = saved_file.read_text()
        assert saved_content == expected_content

    def test_open_content_for_reading_fd(self, temp_repo, temp_content):
        file, expected_content = temp_content

        file_hash = hash_file(file)
        save_file_content(temp_repo, file)

        with open_content_for_reading_fd(temp_repo, file_hash) as f:
            saved_content = f.read()

        assert saved_content == expected_content

    def test_save_and_delete_content(self, temp_repo, temp_content):
        file, _ = temp_content

        save_file_content(temp_repo, file)
        file_hash = hash_file(file)

        saved_file_path = temp_repo / f"{file_hash[:2]}/{file_hash}"
        assert saved_file_path.exists()

        delete_content(temp_repo, file_hash)
        assert not saved_file_path.exists()

    def test_concurrent_read_and_write(self, temp_repo, temp_content):
        file, expected_content = temp_content

        def save():
            save_file_content(temp_repo, file)

        def read():
            file_hash = hash_file(file)
            with open_content_for_reading_fd(temp_repo, file_hash) as f:
                assert f.read() == expected_content

        save_thread = threading.Thread(target=save)
        read_thread = threading.Thread(target=read)

        save_thread.start()
        time.sleep(0.1)
        read_thread.start()

        save_thread.join()
        read_thread.join()

    def test_concurrent_writes(self, temp_repo, temp_content):
        file, _ = temp_content

        def save():
            save_file_content(temp_repo, file)

        threads = [threading.Thread(target=save) for _ in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        file_hash = hash_file(file)
        saved_file_path = temp_repo / f"{file_hash[:2]}/{file_hash}"
        assert saved_file_path.exists()

    def test_concurrent_delete(self, temp_repo, temp_content):
        file, _ = temp_content
        file_hash = hash_file(file)

        def save():
            save_file_content(temp_repo, file)

        def delete():
            time.sleep(0.2)
            delete_content(temp_repo, file_hash)

        save_thread = threading.Thread(target=save)
        delete_thread = threading.Thread(target=delete)

        save_thread.start()
        delete_thread.start()

        save_thread.join()
        delete_thread.join()

        saved_file_path = temp_repo / f"{file_hash[:2]}/{file_hash}"
        assert not saved_file_path.exists()
