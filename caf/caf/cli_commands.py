import sys
import os
from pathlib import Path

from libcaf.repository import Repository, RepositoryError
from libcaf import hash_file
from libcaf.constants import DEFAULT_BRANCH
from datetime import datetime


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
    default_branch = kwargs.get('default_branch', DEFAULT_BRANCH)

    try:
        repo.init(default_branch)
        print(f"Initialized empty CAF repository in {repo.repo_path()} on branch {default_branch}")
        return 0
    except FileExistsError:
        print_error(f"CAF repository already exists in {repo.working_dir}")
        return -1

def delete_repo(**kwargs):
    repo = _repo_from_cli_kwargs(kwargs)
    repo.delete_repo()
    print(f"Deleted repository at {repo.repo_path()}")

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

def add_branch(**kwargs):
    repo = _repo_from_cli_kwargs(kwargs)
    branch_name = kwargs['branch_name']
    repo.add_branch(branch_name)

def delete_branch(**kwargs):
    repo = _repo_from_cli_kwargs(kwargs)
    branch_name = kwargs.get('branch_name')

    try:
        repo.delete_branch(branch_name)
        print(f"Branch '{branch_name}' deleted.")
    except RepositoryError as e:
        print_error(str(e))
        return -1

    return 0

def branch_exists(**kwargs):
    repo = _repo_from_cli_kwargs(kwargs)
    branch_name = kwargs.get('branch_name')

    if repo.branch_exists(branch_name):
        print(f"Branch '{branch_name}' exists.")
    else:
        print(f"Branch '{branch_name}' does not exist.")
        return -1

    return 0

def branch(**kwargs):
    repo = _repo_from_cli_kwargs(kwargs)
    branches = repo.list_branches()

    if branches:
        print("Branches:")
        for index, branch in enumerate (branches):
            if branch == repo.head_full_ref().split('/')[-1]:
                print(f" {index+1}. HEAD: {branch}")
            else:
                print(f" {index+1}. {branch}")
    else:
        print("No branches found.")

    return 0

def commit(**kwargs):
    try:
        repo = _repo_from_cli_kwargs(kwargs)
        if not repo.exists():
            raise RepositoryError(f"No repository found at {repo.repo_path()}")

        author = kwargs.get('author')
        message = kwargs.get('message')

        commit_hash = repo.create_commit(author, message)

        print (f"Commit created successfully:\n"
              f"Hash: {commit_hash}\n"
              f"Author: {author}\n"
              f"Message: {message}\n")
        
    except RepositoryError as e:
        print_error(f"Repository error: {e}")
        return -1
    except ValueError as e:
        print_error(f"Input error: {e}")
        return -1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return -1

    return 0

def log(**kwargs) -> int:
    try:
        repo = _repo_from_cli_kwargs(kwargs)
        if not repo.exists():
            raise RepositoryError(f"No repository found at {repo.repo_path()}")

        commit_history = list(repo.get_commit_history())
        if not commit_history:
            print("No commits in the repository.")
            return 0

        print("Commit History:\n")
        for commit_hash, commit in commit_history:
            print(f"Commit: {commit_hash}")
            print(f"Author: {commit.author}")
            commit_date = datetime.fromtimestamp(commit.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            print(f"Date: {commit_date}\n")
            for line in commit.message.splitlines():
                print(f"    {line}")
            print("\n" + "-" * 50 + "\n")

    except Exception as e:
        print_error(f"Error executing log command: {e}")
        return -1

    return 0
