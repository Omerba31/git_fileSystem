from caf import cli_commands
from libcaf import hash_file,open_content_for_reading,save_file_content
from libcaf.constants import DEFAULT_REPO_DIR, OBJECTS_SUBDIR, HEAD_FILE, REFS_DIR, HEADS_DIR, DEFAULT_BRANCH
import pytest


@pytest.fixture
def temp_content_length() -> int:
    return 100

@pytest.fixture
def initialized_temp_repo(temp_repo):
    assert cli_commands.init(working_dir_path=temp_repo, repo_dir=DEFAULT_REPO_DIR) == 0
    return temp_repo

class TestCLICommands:

    @pytest.mark.parametrize("branch_name", [DEFAULT_BRANCH, "develop"])
    def test_init_repository(self, temp_repo, branch_name):
        assert cli_commands.init(working_dir_path=temp_repo, repo_dir=DEFAULT_REPO_DIR, default_branch=branch_name) == 0
        assert cli_commands.init(working_dir_path=temp_repo, repo_dir=DEFAULT_REPO_DIR, default_branch=branch_name) == -1

        repo_path = temp_repo / DEFAULT_REPO_DIR
        main_branch = repo_path / REFS_DIR / HEADS_DIR / branch_name
        head_file = repo_path / HEAD_FILE

        assert repo_path.exists()
        assert main_branch.exists()
        assert main_branch.stat().st_size == 0
        assert head_file.exists()
        assert head_file.read_text() == f"ref: {REFS_DIR / HEADS_DIR / branch_name}"

    def test_hash_file_no_flag(self, capsys, initialized_temp_repo, temp_content):
        temp_file, expected_content = temp_content

        result = cli_commands.cli_hash_file(path=temp_file, write=False)
        assert result == 0
        
        expected_hash = hash_file(temp_file)
        output = capsys.readouterr()
        assert f"Hash: {expected_hash}" in output.out

    def test_hash_file_with_flag(self, capsys, initialized_temp_repo, temp_content):
        temp_file, expected_content = temp_content

        result = cli_commands.cli_hash_file(path=temp_file,working_dir_path=initialized_temp_repo, repo_dir=DEFAULT_REPO_DIR, write=True)
        assert result == 0
        expected_hash = hash_file(temp_file)

        output = capsys.readouterr()
        assert f"Hash: {expected_hash}" in output.out
        assert f"Saved file {temp_file} to CAF repository" in output.out

        with open_content_for_reading(initialized_temp_repo / DEFAULT_REPO_DIR / OBJECTS_SUBDIR, expected_hash) as f:
            saved_content = f.read()

        assert saved_content == expected_content

    def test_hash_file_not_exist(self, capsys, initialized_temp_repo):
        non_existent_file = initialized_temp_repo / "non_existent_file.txt"

        result = cli_commands.cli_hash_file(path=non_existent_file, write=True)
        assert result == -1

        output = capsys.readouterr()
        assert f"File {non_existent_file} does not exist." in output.err

    def test_hash_file_already_exists_in_repo(self, capsys, initialized_temp_repo):
        temp_file = initialized_temp_repo / "test_file.txt"
        temp_file.write_text("This is a test file.")

        cli_commands.cli_hash_file(path=temp_file, working_dir_path=initialized_temp_repo, repo_dir=DEFAULT_REPO_DIR, write=True)
        result = cli_commands.cli_hash_file(path=temp_file, working_dir_path=initialized_temp_repo, repo_dir=DEFAULT_REPO_DIR, write=True)
        assert result == 0

        output = capsys.readouterr()
        assert "Hash: " in output.out

    def test_hash_file_with_no_repo(self, capsys, temp_repo):
        temp_file = temp_repo / "test_file.txt"
        temp_file.write_text("This is a test file.")

        result = cli_commands.cli_hash_file(path=temp_file, working_dir_path=temp_repo, repo_dir=DEFAULT_REPO_DIR, write=True)
        assert result == -1

        output = capsys.readouterr()
        assert f"Failed to save" in output.err

    def test_empty_branch_handling(self, initialized_temp_repo):
        repo_path = initialized_temp_repo / DEFAULT_REPO_DIR
        branch_path = repo_path / REFS_DIR / HEADS_DIR / DEFAULT_BRANCH
        head_file = repo_path / HEAD_FILE

        assert branch_path.exists()
        assert branch_path.stat().st_size == 0

        with branch_path.open() as f:
            content = f.read()
        assert content == ""

        assert head_file.exists()
        assert head_file.read_text() == f"ref: {REFS_DIR / HEADS_DIR / DEFAULT_BRANCH}"

    def test_add_branch(self, initialized_temp_repo):
        cli_commands.add_branch(working_dir_path=initialized_temp_repo, repo_dir=DEFAULT_REPO_DIR, branch_name="feature")

        branch_path = initialized_temp_repo / DEFAULT_REPO_DIR / REFS_DIR / HEADS_DIR / "feature"
        assert branch_path.exists()

    def test_delete_branch(self, initialized_temp_repo):
        cli_commands.add_branch(working_dir_path=initialized_temp_repo, repo_dir=DEFAULT_REPO_DIR, branch_name="feature")

        result = cli_commands.delete_branch(working_dir_path=initialized_temp_repo, repo_dir=DEFAULT_REPO_DIR, branch_name="feature")
        assert result == 0

        branch_path = initialized_temp_repo / DEFAULT_REPO_DIR / REFS_DIR / HEADS_DIR / "feature"
        assert not branch_path.exists()

    def test_branch_exists(self, initialized_temp_repo):
        cli_commands.add_branch(working_dir_path=initialized_temp_repo, repo_dir=DEFAULT_REPO_DIR, branch_name="feature")
        result = cli_commands.branch_exists(working_dir_path=initialized_temp_repo, repo_dir=DEFAULT_REPO_DIR, branch_name="feature")
        assert result == 0

    def test_branch(self, initialized_temp_repo, capsys):
        branches = ["branch_1", "branch_2", "branch_3", "branch_4", "branch_5"]
        for branch in branches:
            cli_commands.add_branch(working_dir_path=initialized_temp_repo, repo_dir=DEFAULT_REPO_DIR, branch_name=branch)

        capsys.readouterr()

        result = cli_commands.branch(working_dir_path=initialized_temp_repo, repo_dir=DEFAULT_REPO_DIR)
        assert result == 0

        output = capsys.readouterr().out
        lines = output.splitlines()
        print(lines)

        branch_names = []
        for index, line in enumerate (lines):
            if index != 0:
                branch_names.append(line.strip().split()[-1])

        expected_branches = {"main"} | set(branches)
        assert len(branch_names) == len(expected_branches)
        assert set(branch_names) == expected_branches


