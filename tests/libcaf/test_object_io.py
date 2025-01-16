from libcaf import Commit, hash_object, load_commit, save_commit, load_tree, save_tree, Tree, TreeRecord, TreeRecordType


def test_save_load_commit(temp_repo):
    commit = Commit("treehash123", "Author", "Commit message", 1234567890, "commithash123parent")
    commit_hash = hash_object(commit)

    save_commit(temp_repo, commit)
    loaded_commit = load_commit(temp_repo, commit_hash)

    assert loaded_commit.treeHash == commit.treeHash
    assert loaded_commit.author == commit.author
    assert loaded_commit.message == commit.message
    assert loaded_commit.timestamp == commit.timestamp
    assert loaded_commit.parent == commit.parent
    
def test_save_load_commit_with_none_parent(temp_repo):
    commit_none_parent = Commit("commithash456", "Author", "Commit message", 1234567890, None)
    commit_none_parent_hash = hash_object(commit_none_parent)

    save_commit(temp_repo, commit_none_parent)
    loaded_commit_none_parent = load_commit(temp_repo, commit_none_parent_hash)

    assert loaded_commit_none_parent.treeHash == commit_none_parent.treeHash
    assert loaded_commit_none_parent.author == commit_none_parent.author
    assert loaded_commit_none_parent.message == commit_none_parent.message
    assert loaded_commit_none_parent.timestamp == commit_none_parent.timestamp
    assert loaded_commit_none_parent.parent == commit_none_parent.parent

def test_save_load_tree(temp_repo):
    records = {
        "omer": TreeRecord(TreeRecordType.BLOB, "omer123", "omer"),
        "bar": TreeRecord(TreeRecordType.BLOB, "bar123", "bar"),
        "meshi": TreeRecord(TreeRecordType.BLOB, "meshi123", "meshi"),
    }
    tree = Tree(records)
    tree_hash = hash_object(tree)

    save_tree(temp_repo, tree)
    loaded_tree = load_tree(temp_repo, tree_hash)

    assert list(loaded_tree.get_records().keys()) == sorted(records.keys())
    assert loaded_tree.get_records() == records

def test_tree_creation_sorted():
    records = {
        "omer": TreeRecord(TreeRecordType.BLOB, "omer123", "omer"),
        "bar": TreeRecord(TreeRecordType.BLOB, "bar123", "bar"),
        "meshi": TreeRecord(TreeRecordType.BLOB, "meshi123", "meshi"),
    }
    tree = Tree(records)
    sorted_keys = sorted(records.keys())
    tree_keys = list(tree.get_records().keys())
    assert tree_keys == sorted_keys



