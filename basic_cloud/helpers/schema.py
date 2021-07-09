from pathlib import Path

from pydantic import BaseModel


class PathMeta(BaseModel):
    """
    extra info for a path content
    """
    is_directory: bool


class PathContent(BaseModel):
    """
    a paths content (could be a directory or file)
    """
    name: str
    meta: PathMeta


class Roots(BaseModel):
    """
    the root paths
    """
    shared: str
    home: str


class ApiVersion(BaseModel):
    """
    holds the server version &
    oldest compatible version
    """
    version: str
    oldest_compatible: str


class DirectoryStats(BaseModel):
    """
    holds a paths stats
    """
    path: Path
    bytes_size: int
    file_count: int


class RootStats(BaseModel):
    """
    the roots path stats
    """
    shared: DirectoryStats
    homes: DirectoryStats
