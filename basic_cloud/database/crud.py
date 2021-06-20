from pathlib import Path
from typing import List
from uuid import UUID

from ..helpers.constants import ContentChangeTypes
from ..helpers.paths import hash_path
from .models import ContentChange, User


async def create_user(username: str, hashed_password: str) -> User:
    user = User(username=username, hashed_password=hashed_password.encode())
    await user.save()
    return user


async def get_user_by_username(username: str) -> User:
    return await User.filter(username=username).get_or_none()


async def get_user_by_uuid(user_uuid: UUID) -> User:
    return await User.filter(uuid=user_uuid).get_or_none()


async def create_content_change(
        path: Path,
        change_type: ContentChangeTypes,
        is_dir: bool,
        triggered_by: User = None,
        extra_meta: dict = None) -> ContentChange:
    kwargs = {
        "path_hash": hash_path(path),
        "type_enum": change_type,
        "is_dir": is_dir,
        "triggered_by": triggered_by,
        "extra_meta": extra_meta,
    }
    content_change_row = ContentChange(**kwargs)
    await content_change_row.save()
    return content_change_row


async def get_content_changes_by_path(path: Path) -> List[ContentChange]:
    path_hash = hash_path(path)
    return await ContentChange.filter(path_hash=path_hash).all()
