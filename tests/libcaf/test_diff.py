from libcaf.constants import DEFAULT_REPO_DIR
from libcaf.repository import AddedDiff, ModifiedDiff, MovedFromDiff, MovedToDiff, RemovedDiff, Repository


def split_diffs_by_type(diffs):
    added = [d for d in diffs if isinstance(d, AddedDiff)]
    moved_to = [d for d in diffs if isinstance(d, MovedToDiff)]
    moved_from = [d for d in diffs if isinstance(d, MovedFromDiff)]
    removed = [d for d in diffs if isinstance(d, RemovedDiff)]
    modified = [d for d in diffs if isinstance(d, ModifiedDiff)]

    return added, modified, moved_to, moved_from, removed


class TestDiff:
    def test_diff_identical_commits(self, temp_repo):
        repo = Repository(temp_repo, DEFAULT_REPO_DIR)
        repo.init()

        file_path = repo.working_dir / "file.txt"
        file_path.write_text("Same content")
        commit_hash = repo.create_commit("Tester", "Initial commit")

        diff_result = repo.diff_commits(commit_hash, commit_hash)

        assert len(diff_result) == 0

    def test_diff_added_file(self, temp_repo):
        repo = Repository(temp_repo, DEFAULT_REPO_DIR)
        repo.init()

        file1 = repo.working_dir / "file1.txt"
        file1.write_text("Content 1")
        commit1 = repo.create_commit("Tester", "Initial commit")

        file2 = repo.working_dir / "file2.txt"
        file2.write_text("Content 2")
        commit2 = repo.create_commit("Tester", "Added file2")

        diff_result = repo.diff_commits(commit1, commit2)
        added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)

        assert len(added) == 1
        assert added[0].record.name == "file2.txt"

        assert len(moved_to) == 0
        assert len(moved_from) == 0
        assert len(removed) == 0
        assert len(modified) == 0

    def test_diff_removed_file(self, temp_repo):
        repo = Repository(temp_repo, DEFAULT_REPO_DIR)
        repo.init()

        file1 = repo.working_dir / "file.txt"
        file1.write_text("Content")
        commit1 = repo.create_commit("Tester", "File created")

        file1.unlink()  # Delete the file.
        commit2 = repo.create_commit("Tester", "File deleted")

        diff_result = repo.diff_commits(commit1, commit2)
        added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)

        assert len(added) == 0
        assert len(moved_to) == 0
        assert len(moved_from) == 0
        assert len(modified) == 0

        assert len(removed) == 1
        assert removed[0].record.name == "file.txt"

    def test_diff_modified_file(self, temp_repo):
        repo = Repository(temp_repo, DEFAULT_REPO_DIR)
        repo.init()

        file1 = repo.working_dir / "file.txt"
        file1.write_text("Old content")
        commit1 = repo.create_commit("Tester", "Original commit")

        file1.write_text("New content")
        commit2 = repo.create_commit("Tester", "Modified file")

        diff_result = repo.diff_commits(commit1, commit2)
        added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)

        assert len(added) == 0
        assert len(moved_to) == 0
        assert len(moved_from) == 0
        assert len(removed) == 0

        assert len(modified) == 1
        assert modified[0].record.name == "file.txt"

    def test_diff_nested_directory(self, temp_repo):
        repo = Repository(temp_repo, DEFAULT_REPO_DIR)
        repo.init()

        subdir = repo.working_dir / "subdir"
        subdir.mkdir()
        nested_file = subdir / "file.txt"
        nested_file.write_text("Initial")
        commit1 = repo.create_commit("Tester", "Commit with subdir")

        nested_file.write_text("Modified")
        commit2 = repo.create_commit("Tester", "Modified nested file")

        diff_result = repo.diff_commits(commit1, commit2)
        added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)

        assert len(added) == 0
        assert len(moved_to) == 0
        assert len(moved_from) == 0
        assert len(removed) == 0

        assert len(modified) == 1
        assert modified[0].record.name == "subdir"
        assert len(modified[0].children) == 1
        assert modified[0].children[0].record.name == "file.txt"

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
        fileB.unlink()  # Remove fileB.
        fileC = dir2 / "fileC.txt"
        fileC.write_text("C1")

        commit2 = repo.create_commit("Tester", "Updated nested commit")

        diff_result = repo.diff_commits(commit1, commit2)
        added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)

        assert len(added) == 0
        assert len(moved_to) == 0
        assert len(moved_from) == 0
        assert len(removed) == 0

        assert len(modified) == 2

        assert modified[0].record.name == "dir1"
        assert len(modified[0].children) == 1
        assert modified[0].children[0].record.name == "fileA.txt"
        assert isinstance(modified[0].children[0], ModifiedDiff)

        assert modified[1].record.name == "dir2"
        assert len(modified[1].children) == 2
        assert modified[1].children[0].record.name == "fileB.txt"
        assert isinstance(modified[1].children[0], RemovedDiff)
        assert modified[1].children[1].record.name == "fileC.txt"
        assert isinstance(modified[1].children[1], AddedDiff)

    def test_diff_moved_file_added_first(self, temp_repo):
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

        fileA.rename(dir2 / "fileC.txt")

        commit2 = repo.create_commit("Tester", "Updated nested commit")

        diff_result = repo.diff_commits(commit1, commit2)
        added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)

        assert len(added) == 0
        assert len(moved_to) == 0
        assert len(moved_from) == 0
        assert len(removed) == 0

        assert len(modified) == 2

        assert modified[0].record.name == "dir1"
        assert len(modified[0].children) == 1

        modified_child = modified[0].children[0]
        assert isinstance(modified_child, MovedToDiff)
        assert modified_child.record.name == "fileA.txt"

        assert isinstance(modified_child.moved_to, MovedFromDiff)
        assert modified_child.moved_to.parent.record.name == "dir2"
        assert len(modified_child.moved_to.parent.children) == 1
        assert modified_child.moved_to.record.name == "fileC.txt"

        assert modified[1].record.name == "dir2"
        assert len(modified[1].children) == 1

        modified_child = modified[1].children[0]
        assert isinstance(modified_child, MovedFromDiff)
        assert modified_child.record.name == "fileC.txt"

        assert isinstance(modified_child.moved_from, MovedToDiff)
        assert modified_child.moved_from.parent.record.name == "dir1"
        assert len(modified_child.moved_from.parent.children) == 1
        assert modified_child.moved_from.record.name == "fileA.txt"

    def test_diff_moved_file_removed_first(self, temp_repo):
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

        fileB.rename(dir1 / "fileC.txt")

        commit2 = repo.create_commit("Tester", "Updated nested commit")

        diff_result = repo.diff_commits(commit1, commit2)
        added, modified, moved_to, moved_from, removed = split_diffs_by_type(diff_result)

        assert len(added) == 0
        assert len(moved_to) == 0
        assert len(moved_from) == 0
        assert len(removed) == 0

        assert len(modified) == 2

        assert modified[0].record.name == "dir1"
        assert len(modified[0].children) == 1

        modified_child = modified[0].children[0]
        assert isinstance(modified_child, MovedFromDiff)
        assert modified_child.record.name == "fileC.txt"

        assert isinstance(modified_child.moved_from, MovedToDiff)
        assert modified_child.moved_from.parent.record.name == "dir2"
        assert len(modified_child.moved_from.parent.children) == 1
        assert modified_child.moved_from.record.name == "fileB.txt"

        assert modified[1].record.name == "dir2"
        assert len(modified[1].children) == 1

        modified_child = modified[1].children[0]
        assert isinstance(modified_child, MovedToDiff)
        assert modified_child.record.name == "fileB.txt"

        assert isinstance(modified_child.moved_to, MovedFromDiff)
        assert len(modified_child.moved_to.parent.children) == 1
        assert modified_child.moved_to.parent.record.name == "dir1"
        assert modified_child.moved_to.record.name == "fileC.txt"
