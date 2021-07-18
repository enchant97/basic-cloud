from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from pydantic.types import UUID4, Json

from ..helpers.constants import ContentChangeTypes


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


class UserModifyAdmin(BaseModel):
    username: Optional[str]
    disabled: Optional[bool]
    is_admin: Optional[bool]


class Token(BaseModel):
    access_token: str
    token_type: str


class ContentChange(BaseModel):
    created_at: datetime
    type_enum: ContentChangeTypes
    triggered_by_id: Optional[UUID4]
    extra_meta: Optional[Json]


class FileShareCreate(BaseModel):
    path: Path
    expires: Optional[datetime]
    uses_left: Optional[int]


class FileShare(BaseModel):
    uuid: UUID4
    expires: Optional[datetime]
    uses_left: Optional[int]
