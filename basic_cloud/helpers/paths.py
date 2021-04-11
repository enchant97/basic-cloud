from pathlib import Path

from pydantic import BaseModel


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
