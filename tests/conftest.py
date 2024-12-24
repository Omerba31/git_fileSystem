from pathlib import Path
from random import choice

from pytest import fixture


def _random_string(length: int) -> str:
    return ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789-_') for _ in range(length)])


@fixture
def temp_repo(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp('test_repo', numbered=True)


@fixture
def temp_content(request, temp_content_length: int) -> tuple[Path, str]:
    factory = request.getfixturevalue('temp_content_file_factory')

    return factory(length=temp_content_length)


@fixture
def temp_content_file_factory(tmp_path_factory, temp_content_length: int) -> callable:
    test_files = tmp_path_factory.mktemp('test_files')

    def _factory(content: str = None, length: int = None) -> tuple[Path, str]:
        if length is None:
            length = temp_content_length
        if content is None:
            content = _random_string(length)

        file = test_files / _random_string(10)
        with open(file, 'w') as f:
            print(f'{content=}')
            f.write(content)

        return file, content

    return _factory
