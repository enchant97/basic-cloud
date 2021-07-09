import zipfile
from hashlib import sha256
from io import BytesIO
from pathlib import Path

from .exceptions import PathNotExists
from .schema import PathContent, PathMeta


def relative_dir_contents(root_path: Path):
    for path in root_path.glob("*"):
        is_dir = path.is_dir()
        path = path.relative_to(root_path)
        yield PathContent(
            name=str(path).replace("\\", "/"),
            meta=PathMeta(is_directory=is_dir),
        )


def create_user_home_dir(username: str, homes_path: Path):
    homes_path.joinpath(username).mkdir(exist_ok=True)


def create_root_path(
        root_path: Path,
        homes_path: Path,
        shared_path: Path,
        username: str) -> Path:

    if root_path.parts[0] != shared_path.name\
            and root_path.parts[0:2] != (homes_path.name, username):
        raise PathNotExists("unknown root directory")

    parts = root_path.parts[1:]
    if root_path.parts[0] == shared_path.name:
        # must be the shared directory
        if parts:
            root_path = shared_path.joinpath(*parts)
        else:
            root_path = shared_path
    else:
        # must be a user home directory
        if parts:
            root_path = homes_path.joinpath(*parts)
        else:
            root_path = homes_path
    return root_path


def is_root_path(
        absolute_path: Path,
        homes_path: Path,
        shared_path: Path,
        username: str) -> bool:
    """
    checks if the absolute path given is a root path (home or shared)

        :param absolute_path: the path to check
        :param homes_path: the path to the homes directory
        :param shared_path: the path to the shared directory
        :param username: the username
        :return: whether path is just a root path
    """
    if (absolute_path == shared_path or
            absolute_path == homes_path or
            absolute_path == homes_path.joinpath(username)):
        return True
    return False


def create_zip(root_path: Path) -> BytesIO:
    file_obj = BytesIO()
    with zipfile.ZipFile(
            file_obj, mode="w",
            compression=zipfile.ZIP_STORED,
            compresslevel=None) as zip_obj:
        for file_path in root_path.rglob("*"):
            zip_obj.write(file_path, file_path.relative_to(root_path))
    file_obj.seek(0)
    return file_obj


def hash_path(path: Path) -> bytes:
    """
    hash a pathlib Path object, uses sha256

        :param path: the path to hash
        :return: the digest
    """
    return sha256(str(path).encode()).digest()


def calculate_directory_size(root_path: Path) -> int:
    """
    calculates the size in bytes of a directory and its contents

        :param root_path: the root directory to calculate
        :return: the calculated size in bytes
    """
    return sum(f.stat().st_size for f in root_path.glob('**/*') if f.is_file())


def calculate_directory_file_count(root_path: Path) -> int:
    """
    calculates the file count for a directory

        :param root_path: the root directory to calculate
        :return: the file count
    """
    return sum(1 for f in root_path.glob('**/*') if f.is_file())
