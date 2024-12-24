from pytest import raises

from libcaf import Blob, Commit, Tree, TreeRecord, TreeRecordType, computeHash, compute_hash


class TestHashing:
    def test_compute_hash_non_existent_file(self):
        with raises(FileNotFoundError):
            compute_hash("test_compute_hash_non_existent_file.txt")

    def test_commit_hash(self):
        commit = Commit("1234567890abcdef", "Author", "Initial commit", 1234567890,"3234567890abcdef")
        commit_hash = computeHash(commit)

        assert commit_hash is not None
        assert len(commit_hash) == 40
        
    def test_commit_hash_parent_none(self):
        commit = Commit("1234567890abcdef", "Author", "Initial commit", 1234567890,None)
        commit_hash = computeHash(commit)

        assert commit_hash is not None
        assert len(commit_hash) == 40

    def test_tree_hash(self):
        record1 = TreeRecord(TreeRecordType.TREE, "1234567890abcdef", "record1")
        record2 = TreeRecord(TreeRecordType.BLOB, "abcdef1234567890", "record2")

        tree = Tree({"record1": record1, "record2": record2})
        tree_hash = computeHash(tree)

        assert tree_hash is not None
        assert len(tree_hash) == 40

    def test_same_blob_objects_get_same_hash(self):
        blob1 = Blob("1234567890abcdef")
        blob2 = Blob("1234567890abcdef")

        assert computeHash(blob1) == computeHash(blob2)

    def test_same_commit_objects_get_same_hash(self):
        commit1 = Commit("1234567890abcdef", "Author", "Initial commit", 1234567890, "aaabb12")
        commit2 = Commit("1234567890abcdef", "Author", "Initial commit", 1234567890,"aaabb12")

        assert computeHash(commit1) == computeHash(commit2)

    def test_same_commit_objects_get_same_hash_parent_none(self):
        commit1 = Commit("1234567890abcdef", "Author", "Initial commit", 1234567890, None)
        commit2 = Commit("1234567890abcdef", "Author", "Initial commit", 1234567890,None)

        assert computeHash(commit1) == computeHash(commit2)
    def test_same_tree_objects_get_same_hash(self):
        record1 = TreeRecord(TreeRecordType.TREE, "1234567890abcdef", "record1")
        record2 = TreeRecord(TreeRecordType.BLOB, "abcdef1234567890", "record2")

        tree1 = Tree({"record1": record1, "record2": record2})
        tree2 = Tree({"record1": record1, "record2": record2})

        assert computeHash(tree1) == computeHash(tree2)

    def test_different_hashes_for_different_blobs(self):
        blob1 = Blob("1234567890abcdef")
        blob2 = Blob("abcdef1234567890")

        assert computeHash(blob1) != computeHash(blob2)

    def test_different_hashes_for_different_trees(self):
        record1 = TreeRecord(TreeRecordType.TREE, "1234567890abcdef", "record1")
        record2 = TreeRecord(TreeRecordType.BLOB, "abcdef1234567890", "record2")
        record3 = TreeRecord(TreeRecordType.TREE, "fedcba0987654321", "record3")

        tree1 = Tree({"record1": record1, "record2": record2})
        tree2 = Tree({"record1": record1, "record2": record3})

        assert computeHash(tree1) != computeHash(tree2)

    def test_different_hashes_for_different_commits(self):
        commit1 = Commit("1234567890abcdef", "Author1", "Initial commit", 1234567890,None)
        commit2 = Commit("abcdef1234567890", "Author2", "Second commit", 1234567891,"2134567890abcdef")

        assert computeHash(commit1) != computeHash(commit2)

    def test_different_hashes_for_different_parent_commits(self):
        commit1 = Commit("1234567890abcdef", "Author", "Commit message", 1234567890, "parenthash1")
        commit2 = Commit("1234567890abcdef", "Author", "Commit message", 1234567890, "parenthash2")

        hash1 = computeHash(commit1)
        hash2 = computeHash(commit2)

        assert hash1 != hash2, "Hashes for commits with different parent hashes should not match"
        
    def test_different_hashes_for_different_parent_commits_one_none(self):
        # Create two commits that differ only by the parent hash
        commit1 = Commit("1234567890abcdef", "Author", "Commit message", 1234567890, "parenthash1")
        commit2 = Commit("1234567890abcdef", "Author", "Commit message", 1234567890, None)

        # Compute the hash for both commits
        hash1 = computeHash(commit1)
        hash2 = computeHash(commit2)

        # Verify the hashes are different
        assert hash1 != hash2, "Hashes for commits with different parent hashes one none should not match"