import os
import shutil
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.exceptions import DoesNotExist, IntegrityError

from ..config import get_settings
from ..database import crud, models, schema
from ..helpers import auth
from ..helpers.auth import (get_current_admin_user, get_current_user,
                            get_password_hash)
from ..helpers.paths import create_user_home_dir

router = APIRouter()


@router.get(
    "",
    response_model=list[schema.User],
    description="get all users")
async def get_all_users(curr_user: models.User = Depends(get_current_admin_user)):
    return await crud.get_all_users()


@router.post("", response_model=schema.User)
async def create_account(
        new_user: schema.UserCreate):
    try:
        if not get_settings().SIGNUPS_ALLOWED:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="signups are disabled",
            )
        pass_hash = get_password_hash(new_user.password)
        create_user_home_dir(new_user.username, get_settings().HOMES_PATH)
        return await crud.create_user(new_user.username, pass_hash)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already taken",
        ) from None


@router.get("/me", response_model=schema.User)
async def get_me(user: models.User = Depends(auth.get_current_user)):
    return user


@router.delete(
    "/users/{user_uuid}",
    description="delete a user")
async def delete_user(
    user_uuid: UUID,
    curr_user: models.User = Depends(get_current_user)):
    try:
        if curr_user.uuid != user_uuid and not curr_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not admin",
            )
        username = (await crud.get_user_by_uuid(user_uuid)).username
        await crud.delete_user_by_uuid(user_uuid)
        shutil.rmtree(get_settings().HOMES_PATH.joinpath(username))

    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user with that UUID does not exist"
        )


@router.patch(
    "/users/{user_uuid}",
    description="modify a users account details")
async def modify_user(
        user_uuid: UUID,
        modifications: schema.UserModifyAdmin,
        curr_user: models.User = Depends(get_current_user)):
    try:
        if curr_user.uuid != user_uuid and not curr_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not admin",
            )

        if modifications.is_admin is not None and not curr_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not admin",
            )

        # user wants to change username
        if modifications.username:
            user = await crud.get_user_by_uuid(user_uuid)
            if not user: raise DoesNotExist()

            os.rename(
                get_settings().HOMES_PATH.joinpath(user.username),
                get_settings().HOMES_PATH.joinpath(modifications.username)
            )

        modifications = modifications.dict(exclude_unset=True)
        await crud.update_user_by_uuid(user_uuid, modifications)
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user with that UUID does not exist"
        )
