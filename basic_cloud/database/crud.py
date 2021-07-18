from datetime import datetime
from pathlib import Path
from typing import List
from uuid import UUID

from ..helpers.constants import ContentChangeTypes
from .models import ContentChange, FileShare, User

# USER CRUD


async def create_user(username: str, hashed_password: str, is_admin: bool = False) -> User:
    user = User(
        username=username,
        hashed_password=hashed_password.encode(),
        is_admin=is_admin,
    )
    await user.save()
    return user


async def create_default_admin(username: str, hashed_password: str) -> User:
    defaults = {
        "hashed_password": hashed_password.encode(),
        "is_admin": True,
    }
    return (await User.get_or_create(defaults, username=username))[0]


async def get_all_users() -> List[User]:
    return await User.all()


async def get_user_by_username(username: str) -> User:
    return await User.filter(username=username).get_or_none()


async def get_user_by_uuid(user_uuid: UUID) -> User:
    return await User.filter(uuid=user_uuid).get_or_none()


async def update_user_by_uuid(user_uuid: UUID, data: dict) -> User:
    user = await User.filter(uuid=user_uuid).get()
    user.update_from_dict(data)
    await user.save()
    return user


async def delete_user_by_uuid(user_uuid: UUID):
    await User.filter(uuid=user_uuid).delete()

# CONTENT CHANGE CRUD


async def create_content_change(
        path: Path,
        change_type: ContentChangeTypes,
        is_dir: bool,
        triggered_by: User = None,
        extra_meta: dict = None) -> ContentChange:
    kwargs = {
        "path_hash": path,
        "type_enum": change_type,
        "is_dir": is_dir,
        "triggered_by": triggered_by,
        "extra_meta": extra_meta,
    }
    content_change_row = ContentChange(**kwargs)
    await content_change_row.save()
    return content_change_row


async def get_content_changes_by_path(path: Path) -> List[ContentChange]:
    return await ContentChange.filter(path_hash=path).all()

# FILE SHARE CRUD


async def create_file_share(filepath: Path, expires: datetime, uses_left: int) -> FileShare:
    file_share = FileShare(path=filepath, expires=expires, uses_left=uses_left)
    await file_share.save()
    return file_share


async def get_file_share_by_uuid(share_uuid: UUID) -> FileShare:
    return await FileShare.filter(uuid=share_uuid).get()


async def get_shares_by_filepath(filepath: Path) -> List[FileShare]:
    return await FileShare.filter(path=filepath).all()


async def delete_file_share(share_uuid: UUID):
    await FileShare.filter(uuid=share_uuid).delete()
