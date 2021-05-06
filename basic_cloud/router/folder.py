import base64
from pathlib import Path
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse, StreamingResponse

from ..config import get_settings
from ..database import models
from ..helpers.auth import get_current_active_user
from ..helpers.exceptions import PathNotExists
from ..helpers.paths import (PathContent, Roots, create_root_path, create_zip,
                             relative_dir_contents)

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
    "/roots",
    response_model=Roots,
    description="get the root directories")
async def get_roots(curr_user: models.User = Depends(get_current_active_user)):
    share_path = get_settings().SHARED_PATH.name
    home_path = str(Path(get_settings().HOMES_PATH.name)\
        .joinpath(curr_user.username))
    return Roots(shared=share_path, home=home_path)


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
    return directory


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
        directory = create_root_path(
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

    if not directory.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="directory must exist",
        )
    if not directory.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="path must be a directory",
        )

    zip_obj = create_zip(directory)
    return StreamingResponse(zip_obj, media_type="application/zip")
