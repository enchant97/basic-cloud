from pydantic import BaseModel


class ApiVersion(BaseModel):
    version: str
    oldest_compatible: str
