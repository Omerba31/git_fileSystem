import sys
from pathlib import Path

from libcaf.repo import Repo


def print_error(message):
    print(message, file=sys.stderr)


def init(**kwargs) -> int:
    working_dir_path = kwargs['working_dir_path']
    repo_dir = kwargs['repo_dir']

    if isinstance(working_dir_path, str):
        working_dir_path = Path(working_dir_path)
    if isinstance(repo_dir, str):
        repo_dir = Path(repo_dir)

    repo = Repo(working_dir_path, repo_dir)

    try:
        repo.init()
        print(f"Initialized empty CAF repository in {repo.repo_path()}")

        return 0
    except FileExistsError:
        print_error(f"CAF repository already exists in {repo.working_dir}")

        return -1
