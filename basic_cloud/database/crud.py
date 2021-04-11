from uuid import UUID

from .models import User


async def create_user(username: str, hashed_password: str) -> User:
    user = User(username=username, hashed_password=hashed_password.encode())
    await user.save()
    return user


async def get_user_by_username(username: str) -> User:
    return await User.filter(username=username).get_or_none()


async def get_user_by_uuid(user_uuid: UUID) -> User:
    return await User.filter(uuid=user_uuid).get_or_none()
