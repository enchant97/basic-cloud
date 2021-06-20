import base64
from pathlib import Path

import aiofiles
from fastapi import (APIRouter, Body, Depends, Form, HTTPException, UploadFile,
                     status)
from fastapi.param_functions import File, Form
from fastapi.responses import FileResponse

from ..config import get_settings
from ..database import crud, models
from ..helpers.auth import get_current_active_user
from ..helpers.constants import ContentChangeTypes
from ..helpers.exceptions import PathNotExists
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
