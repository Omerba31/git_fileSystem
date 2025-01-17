from pathlib import Path
import shutil

import libcaf
from libcaf.constants import OBJECTS_SUBDIR, DEFAULT_BRANCH, REFS_DIR, HEADS_DIR, HEAD_FILE

class RepositoryError(Exception):
    pass


class Repository:
    def __init__(self, working_dir: Path, repo_dir: Path):
        self.working_dir = working_dir
        self.repo_dir = repo_dir

    def repo_path(self) -> Path:
        return self.working_dir / self.repo_dir

    def objects_dir(self) -> Path:
        return self.repo_path() / OBJECTS_SUBDIR

    def heads_dir(self) -> Path:
        return self.repo_path() / REFS_DIR / HEADS_DIR

    def head_file(self) -> Path:
        return self.repo_path() / HEAD_FILE

    def exists(self) -> bool:
        return self.repo_path().exists()

    def head_full_ref(self) -> str:
        with self.head_file().open() as head_file:
            return head_file.read().split(':')[-1].strip()

    @staticmethod
    def requires_repo(func):
        def _verify_repo(self, *args, **kwargs):
            if not self.exists():
                raise RepositoryError(f'Repository not initialized at {self.repo_path()}')

            return func(self, *args, **kwargs)

        return _verify_repo

    def init(self, default_branch: str = DEFAULT_BRANCH) -> None:
        repo_path = self.repo_path()

        repo_path.mkdir(parents=True)
        self.objects_dir().mkdir()
        heads_dir = self.heads_dir()
        heads_dir.mkdir(parents=True)

        (heads_dir / default_branch).touch()

        with self.head_file().open('w') as head_file:
            head_file.write(f"ref: {REFS_DIR/HEADS_DIR/default_branch}")

    @requires_repo
    def delete_repo(self) -> None:
        repo_path = self.repo_path()
        if repo_path.exists():
            shutil.rmtree(repo_path)
        else:
            raise RepositoryError(f'Repository not found at {repo_path}')

    @requires_repo
    def save_file_content(self, file: Path) -> None:
        libcaf.save_file_content(self.objects_dir(), file)

    @requires_repo
    def add_branch(self, branch_name: str) -> None:
        branch_path = self.heads_dir() / branch_name
        if branch_path.exists():
            print(f"Branch {branch_name} already exists.")
        else:
            branch_path.touch()
            print (f"Branch {branch_name} created.")

    @requires_repo
    def delete_branch(self, branch_name: str) -> None:
        branch_path = self.heads_dir() / branch_name
        if not branch_path.exists():
            raise RepositoryError(f"Branch '{branch_name}' does not exist.")
        if len(self.list_branches()) == 1:
            raise RepositoryError(f"Cannot delete the last branch '{branch_name}'.")
        branch_path.unlink()

    @requires_repo
    def branch_exists(self, branch_name: str) -> bool:
        return (self.heads_dir() / branch_name).exists()

    @requires_repo
    def list_branches(self) -> list:
        return [x.name for x in self.heads_dir().iterdir() if x.is_file()]