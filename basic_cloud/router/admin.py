import os
import shutil
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.exceptions import DoesNotExist

from ..config import get_settings
from ..database import crud, models, schema
from ..helpers.auth import get_current_admin_user
from ..helpers.paths import (calculate_directory_file_count,
                             calculate_directory_size)
from ..helpers.schema import DirectoryStats, RootStats

router = APIRouter()


@router.get(
    "/stats/roots",
    response_model=RootStats,
    description="get the directory root stats")
async def root_stats(curr_user: models.User = Depends(get_current_admin_user)):
    share_path = get_settings().SHARED_PATH
    home_path = get_settings().HOMES_PATH
    return RootStats(
        shared=DirectoryStats(
            path=share_path.name,
            bytes_size=calculate_directory_size(share_path),
            file_count=calculate_directory_file_count(share_path),
        ),
        homes=DirectoryStats(
            path=home_path.name,
            bytes_size=calculate_directory_size(home_path),
            file_count=calculate_directory_file_count(home_path),
        ),
    )


@router.get(
    "/users",
    response_model=List[schema.User],
    description="get all users")
async def get_all_users(curr_user: models.User = Depends(get_current_admin_user)):
    return await crud.get_all_users()


@router.patch(
    "/users/{user_uuid}",
    description="modify a users account details")
async def modify_user(
        user_uuid: UUID,
        modifications: schema.UserModifyAdmin,
        curr_user: models.User = Depends(get_current_admin_user)):
    try:
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


@router.delete(
    "/users/{user_uuid}",
    description="delete a user")
async def delete_user(
    user_uuid: UUID,
    curr_user: models.User = Depends(get_current_admin_user)):
    try:
        username = (await crud.get_user_by_uuid(user_uuid)).username
        await crud.delete_user_by_uuid(user_uuid)
        shutil.rmtree(get_settings().HOMES_PATH.joinpath(username))

    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user with that UUID does not exist"
        )
