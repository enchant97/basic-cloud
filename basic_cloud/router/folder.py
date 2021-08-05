import base64
import binascii
import shutil
from pathlib import Path
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse, StreamingResponse

from ..config import get_settings
from ..database import crud, models, schema
from ..helpers.auth import get_current_active_user
from ..helpers.constants import ContentChangeTypes
from ..helpers.exceptions import PathNotExists
from ..helpers.paths import (create_root_path, create_zip, is_root_path,
                             relative_dir_contents)
from ..helpers.schema import PathContent, Roots
from ..shared import content_changed

router = APIRouter()


@router.post(
    "/contents",
    response_model=List[PathContent],
    description="get a specific directory content")
async def get_directory_contents(
        directory: Path = Body(..., embed=True),
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
            detail="directory must exist",
        )
    if not root_path.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="path must be a directory",
        )
    return relative_dir_contents(root_path)


@router.get(
    "/{folder_path}/history",
    response_model=List[schema.ContentChange],
    description="get history for folder")
async def get_history_by_folder(
        folder_path: str,
        curr_user: models.User = Depends(get_current_active_user)):
    try:
        folder_path = base64.b64decode(folder_path).decode()
        folder_path = Path(folder_path)

        full_path = create_root_path(
            folder_path,
            get_settings().HOMES_PATH,
            get_settings().SHARED_PATH,
            curr_user.username,
        )
        if not full_path.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="directory must exist",
            )

        if not full_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cannot be a file",
            )
        return await crud.get_content_changes_by_path(folder_path)

    except PathNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unknown root directory",
        ) from None

    except (ValueError, binascii.Error):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="malformed base64 filename"
        ) from None


@router.get(
    "/roots",
    response_model=Roots,
    description="get the root directories")
async def get_roots(curr_user: models.User = Depends(get_current_active_user)):
    share_path = get_settings().SHARED_PATH.name
    home_path = str(Path(get_settings().HOMES_PATH.name)\
        .joinpath(curr_user.username))
    return Roots(
        shared=share_path.replace("\\", "/"),
        home=home_path.replace("\\", "/"),
    )


@router.post(
    "/mkdir",
    response_class=PlainTextResponse,
    description="create a directory")
async def create_directory(
        directory: Path = Body(..., embed=True),
        name: Path = Body(..., embed=True),
        curr_user: models.User = Depends(get_current_active_user)):
    directory = directory.joinpath(name)
    try:
        full_path = create_root_path(
            directory,
            get_settings().HOMES_PATH,
            get_settings().SHARED_PATH,
            curr_user.username,
        )
    except PathNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unknown root directory",
        )

    full_path.mkdir(parents=True, exist_ok=True)

    await content_changed(
        directory,
        ContentChangeTypes.CREATION,
        True,
        curr_user
    )
    return directory


@router.delete(
    "/rm",
    description="delete a directory")
async def delete_directory(
        directory: Path = Body(..., embed=True),
        curr_user: models.User = Depends(get_current_active_user)):

    try:
        full_path = create_root_path(
            directory,
            get_settings().HOMES_PATH,
            get_settings().SHARED_PATH,
            curr_user.username,
        )
        if is_root_path(
                full_path,
                get_settings().HOMES_PATH,
                get_settings().SHARED_PATH,
                curr_user.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cannot delete root directory",
            )
        if not full_path.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="directory must exist",
            )
        if not full_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="path must be a directory",
            )

        shutil.rmtree(full_path)

        await content_changed(
            directory,
            ContentChangeTypes.DELETION,
            True,
            curr_user
        )

    except PathNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unknown root directory",
        )


@router.get(
    "/download/{directory}",
    response_class=StreamingResponse,
    description="download as a zip, directory must be encoded as base64")
async def download_zip(
        directory: str,
        curr_user: models.User = Depends(get_current_active_user)):
    directory = base64.b64decode(directory).decode()
    directory = Path(directory)

    try:
        full_path = create_root_path(
            directory,
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
            detail="directory must exist",
        )
    if not full_path.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="path must be a directory",
        )

    zip_obj = create_zip(full_path)

    await content_changed(
        directory,
        ContentChangeTypes.DOWNLOAD,
        True,
        curr_user
    )
    return StreamingResponse(zip_obj, media_type="application/zip")
