from libcaf import Commit, computeHash, load_commit, save_commit


def test_save_load_commit(temp_repo):
    commit = Commit("treehash123", "Author", "Commit message", 1234567890)
    commit_hash = computeHash(commit)

    save_commit(temp_repo, commit)
    loaded_commit = load_commit(temp_repo, commit_hash)

    assert loaded_commit.treeHash == commit.treeHash
    assert loaded_commit.author == commit.author
    assert loaded_commit.message == commit.message
    assert loaded_commit.timestamp == commit.timestamp
