import sys
from pathlib import Path

from libcaf.repository import Repository, RepositoryError

from libcaf import hash_file

def print_error(message):
    print(message, file=sys.stderr)

def _repo_from_cli_kwargs(kwargs) -> Repository:
    working_dir_path = kwargs['working_dir_path']
    repo_dir = kwargs['repo_dir']

    if isinstance(repo_dir, str):
        repo_dir = Path(repo_dir)

    if isinstance(working_dir_path, str):
        working_dir_path = Path(working_dir_path)

    return Repository(working_dir_path, repo_dir)

def init(**kwargs) -> int:
    repo = _repo_from_cli_kwargs(kwargs)

    try:
        repo.init()
        print(f"Initialized empty CAF repository in {repo.repo_path()}")
        return 0
    except FileExistsError:
        print_error(f"CAF repository already exists in {repo.working_dir}")
        return -1

def cli_hash_file(**kwargs) -> int:
    path = Path(kwargs['path'])

    if not path.exists():
        print_error(f"File {path} does not exist.")
        return -1

    file_hash = hash_file(path)
    print(f"Hash: {file_hash}")

    if kwargs.get('write', False):
        repo = _repo_from_cli_kwargs(kwargs)

        try:
            repo.save_file_content(path)
            print(f"Saved file {path} to CAF repository")
        except RepositoryError:
            print_error(f"Failed to save file {path} to CAF repository, is the repository initialized?")
            return -1
        except Exception as e:
            print_error(f"Unexpected error saving file {path} to CAF repository: {e}")
            return -1

    return 0
