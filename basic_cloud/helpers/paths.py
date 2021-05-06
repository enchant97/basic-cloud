import zipfile
from io import BytesIO
from pathlib import Path

from pydantic import BaseModel

from .exceptions import PathNotExists


class PathMeta(BaseModel):
    is_directory: bool


class PathContent(BaseModel):
    name: str
    meta: PathMeta


class Roots(BaseModel):
    shared: str
    home: str


def relative_dir_contents(root_path: Path):
    for path in root_path.glob("*"):
        is_dir = path.is_dir()
        path = path.relative_to(root_path)
        yield PathContent(name=str(path), meta=PathMeta(is_directory=is_dir))


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
