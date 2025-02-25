import threading
import time

from pytest import mark, raises
from libcaf import hash_file, delete_content, open_content_for_reading, save_file_content, load_commit, hash_object
from libcaf.constants import DEFAULT_REPO_DIR
from libcaf.repository import Repository

class TestRepo:
    def test_open_non_existent_file(self, temp_repo):
        non_existent_hash = "deadbeef" + "0" * 32

        with raises(ValueError):
            open_content_for_reading(temp_repo, non_existent_hash)

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

    def test_create_commit(self, temp_repo):
        repo = Repository(temp_repo, DEFAULT_REPO_DIR)
        repo.init()

        temp_file = repo.working_dir / "test_file.txt"
        temp_file.write_text("This is a test file for commit.")

        repo.save_file_content(temp_file)

        author = "John Doe"
        message = "Initial commit"

        commit_hash = repo.create_commit(author, message)
        commit = load_commit(repo.objects_dir(), commit_hash)

        assert commit.author == author
        assert commit.message == message
        assert commit.treeHash is not None

        head_file = repo.head_file()
        assert head_file.exists()

        head_content = head_file.read_text().strip()
        assert len(head_content) > 0
        assert head_content == commit_hash

        commit_file = repo.objects_dir() / commit_hash[:2] / commit_hash
        assert commit_file.exists()

    def test_create_commit_with_parent(self, temp_repo):
        repo = Repository(temp_repo, DEFAULT_REPO_DIR)
        repo.init()
        head_file = repo.head_file()
        objects_dir = repo.objects_dir()

        temp_file = repo.working_dir / "test_file.txt"
        temp_file.write_text("Initial commit content")
        repo.save_file_content(temp_file)

        author = "John Doe"

        first_commit_hash = repo.create_commit(author, "First commit")
        first_commit = load_commit(objects_dir, first_commit_hash)
        assert first_commit_hash == hash_object(first_commit)

        assert head_file.read_text().strip() == first_commit_hash

        temp_file.write_text("Second commit content")
        repo.save_file_content(temp_file)

        second_commit_hash = repo.create_commit(author, "Second commit")
        second_commit = load_commit(objects_dir, second_commit_hash)
        assert second_commit_hash == hash_object(second_commit)

        assert head_file.read_text().strip() == second_commit_hash
        assert second_commit.parent == first_commit_hash


    def test_save_directory_tree(self, temp_repo):
        repo = Repository(temp_repo, DEFAULT_REPO_DIR)
        repo.init()

        test_dir = repo.working_dir / "test_dir"
        test_dir.mkdir()
        sub_dir = test_dir / "sub_dir"
        sub_dir.mkdir()

        file1 = test_dir / "file1.txt"
        file1.write_text("Content of file1")
        file2 = sub_dir / "file2.txt"
        file2.write_text("Content of file2")
        file3 = sub_dir / "file3.txt"
        file3.write_text("Content of file3")

        tree_hash = repo.save_directory_tree(test_dir)

        assert tree_hash is not None
        assert isinstance(tree_hash, str)
        assert len(tree_hash) > 0

        objects_dir = repo.objects_dir()

        for file_path in [file1, file2, file3]:
            file_blob_hash = hash_object(repo.save_file_content(file_path))
            assert (objects_dir / file_blob_hash[:2] / file_blob_hash).exists()

        assert (objects_dir / tree_hash[:2] / tree_hash).exists()

    def test_get_commit_history(self, temp_repo):
        repo = Repository(temp_repo, DEFAULT_REPO_DIR)
        repo.init()

        temp_file = repo.working_dir / "commit_test.txt"
        temp_file.write_text("Initial commit")
        repo.save_file_content(temp_file)
        commit_hash1 = repo.create_commit("Author", "First commit")

        temp_file.write_text("Second commit")
        repo.save_file_content(temp_file)
        commit_hash2 = repo.create_commit("Author", "Second commit")

        history = list(repo.get_commit_history())
        assert len(history) == 2

        assert history[0][0] == commit_hash2
        assert history[1][0] == commit_hash1


