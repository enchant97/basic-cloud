from pathlib import Path

from pydantic import BaseModel


class ApiVersion(BaseModel):
    version: str
    oldest_compatible: str


class DirectoryStats(BaseModel):
    path: Path
    bytes_size: int
    file_count: int


class RootStats(BaseModel):
    shared: DirectoryStats
    homes: DirectoryStats
