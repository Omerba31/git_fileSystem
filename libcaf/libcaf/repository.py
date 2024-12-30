from pathlib import Path

import libcaf
from libcaf.constants import OBJECTS_SUBDIR




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

    def exists(self) -> bool:
        return self.repo_path().exists()

    @staticmethod
    def requires_repo(func):
        def _verify_repo(self, *args, **kwargs):
            if not self.exists():
                raise RepositoryError(f'Repository not initialized at {self.repo_path()}')

            return func(self, *args, **kwargs)

        return _verify_repo

    def init(self) -> None:
        repo_path = self.repo_path()

        repo_path.mkdir(parents=True)
        self.objects_dir().mkdir()

    @requires_repo
    def save_file(self, file: Path) -> None:
        libcaf.save_content(self.objects_dir(), file)
