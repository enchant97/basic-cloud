from datetime import datetime
from pydantic import BaseModel
from pydantic.types import UUID4


class ModifyBase(BaseModel):
    created_at: datetime
    updated_at: datetime


class User(ModifyBase):
    uuid: UUID4
    username: str
    disabled: bool = False
    is_admin: bool = False


class UserCreate(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
