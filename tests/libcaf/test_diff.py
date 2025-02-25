import pytest
from pathlib import Path
from libcaf.repository import Repository, Diff, DiffType
from libcaf.constants import DEFAULT_REPO_DIR

class TestDiff:
    def test_diff_identical_commits(self, temp_repo):
        repo = Repository(temp_repo, DEFAULT_REPO_DIR)
        repo.init()

        file_path = repo.working_dir / "file.txt"
        file_path.write_text("Same content")
        repo.save_file_content(file_path)
        commit_hash = repo.create_commit("Tester", "Initial commit")

        diff_result = list(repo.diff_commits(commit_hash, commit_hash))

        assert diff_result == []

    def test_diff_added_file(self, temp_repo):
        repo = Repository(temp_repo, DEFAULT_REPO_DIR)
        repo.init()

        file1 = repo.working_dir / "file1.txt"
        file1.write_text("Content 1")
        repo.save_file_content(file1)
        commit1 = repo.create_commit("Tester", "Initial commit")

        file2 = repo.working_dir / "file2.txt"
        file2.write_text("Content 2")
        repo.save_file_content(file2)
        commit2 = repo.create_commit("Tester", "Added file2")

        diff_result = list(repo.diff_commits(commit1, commit2))

        added = [d.name for d in diff_result if d.diff_type == DiffType.ADDED]
        removed = [d.name for d in diff_result if d.diff_type == DiffType.REMOVED]
        modified = [d.name for d in diff_result if d.diff_type == DiffType.MODIFIED]

        assert "file2.txt" in added
        assert removed == []
        assert modified == []

    def test_diff_removed_file(self, temp_repo):
        repo = Repository(temp_repo, DEFAULT_REPO_DIR)
        repo.init()

        file1 = repo.working_dir / "file.txt"
        file1.write_text("Content")
        repo.save_file_content(file1)
        commit1 = repo.create_commit("Tester", "File created")

        file1.unlink()  # Delete the file.
        commit2 = repo.create_commit("Tester", "File deleted")

        diff_result = list(repo.diff_commits(commit1, commit2))
        removed = [d.name for d in diff_result if d.diff_type == DiffType.REMOVED]
        added = [d.name for d in diff_result if d.diff_type == DiffType.ADDED]
        modified = [d.name for d in diff_result if d.diff_type == DiffType.MODIFIED]

        assert "file.txt" in removed
        assert added == []
        assert modified == []

    def test_diff_modified_file(self, temp_repo):
        repo = Repository(temp_repo, DEFAULT_REPO_DIR)
        repo.init()

        file1 = repo.working_dir / "file.txt"
        file1.write_text("Old content")
        repo.save_file_content(file1)
        commit1 = repo.create_commit("Tester", "Original commit")

        file1.write_text("New content")
        repo.save_file_content(file1)
        commit2 = repo.create_commit("Tester", "Modified file")

        diff_result = list(repo.diff_commits(commit1, commit2))
        modified = [d.name for d in diff_result if d.diff_type == DiffType.MODIFIED]
        added = [d.name for d in diff_result if d.diff_type == DiffType.ADDED]
        removed = [d.name for d in diff_result if d.diff_type == DiffType.REMOVED]

        assert "file.txt" in modified
        assert added == []
        assert removed == []

    def test_diff_nested_directory(self, temp_repo):
        repo = Repository(temp_repo, DEFAULT_REPO_DIR)
        repo.init()

        subdir = repo.working_dir / "subdir"
        subdir.mkdir()
        nested_file = subdir / "file.txt"
        nested_file.write_text("Initial")
        repo.save_file_content(nested_file)
        commit1 = repo.create_commit("Tester", "Commit with subdir")

        nested_file.write_text("Modified")
        repo.save_file_content(nested_file)
        commit2 = repo.create_commit("Tester", "Modified nested file")
        diff_result = list(repo.diff_commits(commit1, commit2))

        modified = [d.name for d in diff_result if d.diff_type == DiffType.MODIFIED]
        assert "subdir" in modified or "file.txt" in modified

    def test_diff_nested_trees(self, temp_repo):
        repo = Repository(temp_repo, DEFAULT_REPO_DIR)
        repo.init()

        dir1 = repo.working_dir / "dir1"
        dir1.mkdir()
        fileA = dir1 / "fileA.txt"
        fileA.write_text("A1")

        dir2 = repo.working_dir / "dir2"
        dir2.mkdir()
        fileB = dir2 / "fileB.txt"
        fileB.write_text("B1")

        commit1 = repo.create_commit("Tester", "Initial nested commit")

        fileA.write_text("A2")
        repo.save_file_content(fileA)
        fileB.unlink()  # Remove fileB.
        fileC = dir2 / "fileC.txt"
        fileC.write_text("C1")
        repo.save_file_content(fileC)

        commit2 = repo.create_commit("Tester", "Updated nested commit")
        diff_result = list(repo.diff_commits(commit1, commit2))
        
        modified = [d.name for d in diff_result if d.diff_type == DiffType.MODIFIED]
        assert "dir1" in modified
        assert "dir2" in modified


