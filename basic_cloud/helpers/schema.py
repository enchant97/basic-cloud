from pydantic import BaseModel


class ApiVersion(BaseModel):
    version: str
    oldest_compatible: str


class RootStats(BaseModel):
    shared_size: int
    homes_size: int
