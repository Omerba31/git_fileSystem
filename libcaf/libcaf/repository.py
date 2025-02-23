from pathlib import Path
import shutil

import libcaf
from libcaf.constants import OBJECTS_SUBDIR, DEFAULT_BRANCH, REFS_DIR, HEADS_DIR, HEAD_FILE
from libcaf import Blob, TreeRecord, Commit, TreeRecordType, Tree, save_tree, hash_object, save_commit, load_commit
from collections import deque
from datetime import datetime


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
    def save_file_content(self, file: Path) -> Blob:
        return libcaf.save_file_content(self.objects_dir(), file)

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
    
    @requires_repo
    def save_directory_tree(self, path: Path) -> str:
        if not path.is_dir():
            raise ValueError(f"{path} is not a directory")

        stack = deque([path])
        hashes = {}

        while stack:
            current_path = stack.pop()
            tree_records = {}

            for item in current_path.iterdir():
                if item.is_file():
                    blob = self.save_file_content(item)
                    tree_records[item.name] = TreeRecord(TreeRecordType.BLOB, item.name, blob.hash)
                elif item.is_dir():
                    if item in hashes:  # If the directory has already been processed, use its hash
                        subtree_hash = hashes[item]
                        tree_records[item.name] = TreeRecord(TreeRecordType.TREE, item.name, subtree_hash)
                    else:
                        stack.append(current_path)
                        stack.append(item)
                        break
            else:
                tree = Tree(tree_records)
                save_tree(self.objects_dir(), tree)
                hashes[current_path] = hash_object(tree)

        return hashes[path]
    
    @requires_repo
    def create_commit(self, author: str, message: str) -> str:
        if not author or not message:
            raise ValueError("Both 'author' and 'message' are required.")

        tree_hash = self.save_directory_tree(self.working_dir)

        head_content = self.head_file().read_text().strip()
        parent_hash = None if head_content.startswith("ref:") else head_content

        commit = Commit(tree_hash, author, message, int(datetime.now().timestamp()), parent_hash)

        commit_hash = hash_object(commit)
        save_commit(self.objects_dir(), commit)

        with self.head_file().open("w") as head_file:
            head_file.write(f"{commit_hash}\n")

        return commit_hash
    
    @requires_repo
    def get_commit_history(self, start_commit: str = None):
        try:
            if start_commit is None:
                head_hash = self.head_file().read_text().strip()
            else:
                head_hash = start_commit
        except Exception as e:
            raise RepositoryError(f"Error reading HEAD file: {e}")

        if head_hash.startswith("ref:"):
            return

        current_hash = head_hash
        while current_hash:
            try:
                commit = load_commit(self.objects_dir(), current_hash)
            except Exception as e:
                raise RepositoryError(f"Error loading commit {current_hash}: {e}")
            yield (current_hash, commit)
            current_hash = commit.parent if commit.parent else None

    
    
    
