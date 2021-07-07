from datetime import datetime, timedelta
from typing import Optional, Union
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from ..config import get_settings
from ..database import crud, models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    checks whether the plain-text
    password matches the hashed one

        :param plain_password: the plain-text password
        :param hashed_password: the hashed password
        :return: whether the password matched
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    returns a hash of the
    plain-text password given

        :param password: the plain-text password
        :return: the hashed password
    """
    return pwd_context.hash(password)


async def authenticate_user(
        username: str,
        password: str) -> Union[models.User, bool]:
    """
    checks whether username & password match

        :param username: the username to match
        :param password: the password related to the username
        :return: the user or False if they did not match
    """
    user = await crud.get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password.decode()):
        return False
    return user


def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        get_settings().SECRET_KEY,
        algorithm=get_settings().HASH_ALGORITHM,
        )
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> models.User:
    """
    checks whether the token given
    is valid and returns the user

        :return: the user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            get_settings().SECRET_KEY,
            algorithms=[get_settings().HASH_ALGORITHM],
            )
        user_uuid: str = payload.get("sub")
        if user_uuid is None:
            raise credentials_exception
        user_uuid: UUID = UUID(user_uuid)
    except (ValueError, JWTError):
        raise credentials_exception
    user = await crud.get_user_by_uuid(user_uuid)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
        current_user: models.User = Depends(get_current_user)) -> models.User:
    """
    uses get_current_user and also checks
    whether the account has been disabled

        :return: the user
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
        current_user: models.User = Depends(get_current_user)) -> models.User:
    """
    uses get_current_active_user and also checks
    whether the account has admin access

        :return: the user
    """
    if current_user.is_admin:
        raise HTTPException(status_code=400, detail="Not admin")
    return current_user
