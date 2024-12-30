from caf import cli_commands
from libcaf import compute_hash,open_content,save_content
from libcaf.constants import DEFAULT_REPO_DIR, OBJECTS_SUBDIR
import pytest

@pytest.fixture
def temp_content_length() -> int:
    return 100


class TestCLICommands:
    
    def test_check_init_repository_not_exists(self, capsys, temp_repo):
        result = cli_commands.init(working_dir_path=temp_repo, repo_dir=DEFAULT_REPO_DIR)
        assert result == 0

        repo_path = temp_repo / DEFAULT_REPO_DIR
        assert repo_path.exists()

        output = capsys.readouterr()
        assert f"Initialized empty CAF repository in {repo_path}" in output.out

    def test_check_init_repository_exists(self, capsys, temp_repo):
        repo_path = temp_repo / DEFAULT_REPO_DIR
        repo_path.mkdir()

        result = cli_commands.init(working_dir_path=temp_repo, repo_dir=DEFAULT_REPO_DIR)
        assert result == -1

        output = capsys.readouterr()
        assert f"CAF repository already exists in {temp_repo}" in output.err

    def test_hash_file_no_flag(self, capsys, temp_repo, temp_content):
        cli_commands.init(working_dir_path=temp_repo, repo_dir=DEFAULT_REPO_DIR)

        temp_file, expected_content = temp_content

        result = cli_commands.hash_file(path=temp_file, write=False)
        assert result == 0
        
        expected_hash = compute_hash(temp_file)
        output = capsys.readouterr()
        assert f"Hash: {expected_hash}" in output.out

    def test_hash_file_with_flag(self, capsys, temp_repo, temp_content):
        cli_commands.init(working_dir_path=temp_repo, repo_dir=DEFAULT_REPO_DIR)

        temp_file, expected_content = temp_content

        result = cli_commands.hash_file(path=temp_file,
                                        working_dir_path=temp_repo, repo_dir=DEFAULT_REPO_DIR,
                                        write=True)
        assert result == 0
        expected_hash = compute_hash(temp_file)

        output = capsys.readouterr()
        assert f"Hash: {expected_hash}" in output.out
        assert f"Saved file {temp_file} to CAF repository" in output.out

        # Verify the contents of the file corresponding to the hash
        
        with open_content(temp_repo / DEFAULT_REPO_DIR / OBJECTS_SUBDIR, expected_hash) as f:
            saved_content = f.read()

        assert saved_content == expected_content

    def test_hash_file_not_exist(self, capsys, temp_repo):
        cli_commands.init(working_dir_path=temp_repo, repo_dir=DEFAULT_REPO_DIR)

        non_existent_file = temp_repo / "non_existent_file.txt"

        result = cli_commands.hash_file(path=non_existent_file, write=True)
        assert result == -1

        output = capsys.readouterr()
        assert f"File {non_existent_file} does not exist." in output.err

    def test_hash_file_already_exists_in_repo(self, capsys, temp_repo):
        cli_commands.init(working_dir_path=temp_repo, repo_dir=DEFAULT_REPO_DIR)

        temp_file = temp_repo / "test_file.txt"
        temp_file.write_text("This is a test file.")

        cli_commands.hash_file(path=temp_file,
                               working_dir_path=temp_repo, repo_dir=DEFAULT_REPO_DIR,
                               write=True)

        result = cli_commands.hash_file(path=temp_file,
                                        working_dir_path=temp_repo, repo_dir=DEFAULT_REPO_DIR,
                                        write=True)
        assert result == 0

        output = capsys.readouterr()
        assert "Hash: " in output.out

    def test_hash_file_with_no_repo(self, capsys, temp_repo):
        temp_file = temp_repo / "test_file.txt"
        temp_file.write_text("This is a test file.")

        result = cli_commands.hash_file(path=temp_file,
                                        working_dir_path=temp_repo, repo_dir=DEFAULT_REPO_DIR,
                                        write=True)
        assert result == -1

        output = capsys.readouterr()
        assert f"Failed to save" in output.err