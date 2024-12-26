from caf import cli_commands

repo_dir = '.caf'


class TestCLICommands:
    def test_check_init_repository_not_exists(self, capsys, temp_repo):
        result = cli_commands.init(working_dir_path=temp_repo, repo_dir=repo_dir)
        assert result == 0

        repo_path = temp_repo / repo_dir
        assert repo_path.exists()

        output = capsys.readouterr()
        assert f"Initialized empty CAF repository in {repo_path}" in output.out

    def test_check_init_repository_exists(self, capsys, temp_repo):
        repo_path = temp_repo / repo_dir
        repo_path.mkdir()

        result = cli_commands.init(working_dir_path=temp_repo, repo_dir=repo_dir)
        assert result == -1

        output = capsys.readouterr()
        assert f"CAF repository already exists in {temp_repo}" in output.err
