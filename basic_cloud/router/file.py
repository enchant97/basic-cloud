import base64
from pathlib import Path
from uuid import UUID

import aiofiles
from fastapi import (APIRouter, Body, Depends, Form, HTTPException, UploadFile,
                     status)
from fastapi.param_functions import File, Form
from fastapi.responses import FileResponse
from tortoise import timezone
from tortoise.exceptions import DoesNotExist

from ..config import get_settings
from ..database import crud, models, schema
from ..helpers.auth import get_current_active_user
from ..helpers.constants import ContentChangeTypes
from ..helpers.exceptions import PathNotExists, SharePathInvalid
from ..helpers.paths import create_root_path

router = APIRouter()


@router.delete(
    "/rm",
    description="delete a file")
async def delete_file(
        file_path: Path = Body(..., embed=True),
        curr_user: models.User = Depends(get_current_active_user)):

    try:
        full_path = create_root_path(
            file_path,
            get_settings().HOMES_PATH,
            get_settings().SHARED_PATH,
            curr_user.username,
        )
        if not full_path.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="directory/file must exist",
            )
        if not full_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="path must be a file",
            )

        full_path.unlink(missing_ok=True)

        if get_settings().HISTORY_LOG:
            await crud.create_content_change(
                file_path,
                ContentChangeTypes.DELETION,
                False,
                curr_user,
            )

    except PathNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unknown root directory",
        )


@router.get(
    "/download/{file_path}",
    response_class=FileResponse,
    description="download a file")
async def download_file(
        file_path: str,
        curr_user: models.User = Depends(get_current_active_user)):
    file_path = base64.b64decode(file_path).decode()
    file_path = Path(file_path)

    try:
        full_path = create_root_path(
            file_path,
            get_settings().HOMES_PATH,
            get_settings().SHARED_PATH,
            curr_user.username,
        )
    except PathNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unknown root directory",
        )

    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="directory/file must exist",
        )

    if not full_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cannot be a directory",
        )

    if get_settings().HISTORY_LOG:
        await crud.create_content_change(
            file_path,
            ContentChangeTypes.DOWNLOAD,
            False,
            curr_user,
        )

    return FileResponse(full_path, filename=file_path.name)


@router.post("/upload/overwrite")
async def upload_file_overwrite(
        file: UploadFile = File(...),
        directory: Path = Form(...),
        curr_user: models.User = Depends(get_current_active_user)):
    root_path = directory
    try:
        root_path = create_root_path(
            root_path,
            get_settings().HOMES_PATH,
            get_settings().SHARED_PATH,
            curr_user.username,
        )
    except PathNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unknown root directory",
        )

    if not root_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="directory/file must exist",
        )

    if not root_path.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="cannot be a directory",
        )

    root_path = root_path.joinpath(file.filename)

    # write the file to system
    async with aiofiles.open(root_path, "wb") as fo:
        await fo.write(await file.read())
        await file.close()

    if get_settings().HISTORY_LOG:
        await crud.create_content_change(
            directory.joinpath(file.filename),
            ContentChangeTypes.CREATION,
            False,
            curr_user,
        )

    return {"path": directory.joinpath(file.filename)}


@router.post(
    "/share",
    response_model=schema.FileShare,
    description="create a file share")
async def create_file_share(
        file_share: schema.FileShareCreate,
        curr_user: models.User = Depends(get_current_active_user)):
    try:
        root_path = create_root_path(
            file_share.path,
            get_settings().HOMES_PATH,
            get_settings().SHARED_PATH,
            curr_user.username,
        )
        if not root_path.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="file must exist",
            )

        if not root_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cannot be a directory",
            )

    except PathNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unknown root directory",
        )

    created_row = await crud.create_file_share(
        file_share.path,
        file_share.expires,
        file_share.users_left
    )
    return created_row


@router.delete(
    "/share/{share_uuid}",
    description="delete a file share")
async def delete_file_share(
        share_uuid: UUID,
        curr_user: models.User = Depends(get_current_active_user)):
    try:
        file_share = await crud.get_file_share_by_uuid(share_uuid)
        # makes sure user has access to path
        create_root_path(
            file_share.path,
            get_settings().HOMES_PATH,
            get_settings().SHARED_PATH,
            curr_user.username,
        )
        await crud.delete_file_share(share_uuid)
    except (PathNotExists, DoesNotExist):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="unknown file share uuid"
        ) from None


@router.get(
    "/share/{share_uuid}",
    response_model=schema.FileShare,
    description="get a file shares meta")
async def get_file_share_meta(
        share_uuid: UUID,
        curr_user: models.User = Depends(get_current_active_user)):
    try:
        file_share = await crud.get_file_share_by_uuid(share_uuid)
        # makes sure user has access to path
        create_root_path(
            file_share.path,
            get_settings().HOMES_PATH,
            get_settings().SHARED_PATH,
            curr_user.username,
        )
        return file_share
    except (PathNotExists, DoesNotExist):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="unknown file share uuid"
        ) from None


@router.get(
    "/share/{share_uuid}/download",
    response_class=FileResponse,
    description="get a file shares file")
async def get_file_share_file(share_uuid: UUID):
    try:
        file_share = await crud.get_file_share_by_uuid(share_uuid)

        # make sure share isn't expired or has run out of uses
        if ((file_share.expires is not None and file_share.expires < timezone.now()) or
                (file_share.uses_left is not None and file_share.uses_left < 1)):
            raise SharePathInvalid()

        full_path = create_root_path(
            file_share.path,
            get_settings().HOMES_PATH,
            get_settings().SHARED_PATH,
        )
        if not full_path.exists():
            # remove the share from database as path no longer exists
            await crud.delete_file_share(share_uuid)
            raise PathNotExists()

        if file_share.uses_left is not None:
            # if the share has limited uses subtract one
            file_share.uses_left -= 1
            await file_share.save()

        return FileResponse(full_path, filename=full_path.name)
    except (PathNotExists, DoesNotExist):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="unknown file share uuid"
        ) from None
    except SharePathInvalid:
        # share has either run out of uses or expired
        await crud.delete_file_share(share_uuid)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="unknown file share uuid"
        ) from None
