from pathlib import Path
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, status

from ..config import get_settings
from ..database import models
from ..helpers.auth import get_current_active_user
from ..helpers.exceptions import PathNotExists
from ..helpers.paths import (PathContent, Roots, create_root_path,
                             relative_dir_contents)

router = APIRouter()


@router.post("/contents", response_model=List[PathContent])
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


@router.get("/roots", response_model=Roots)
async def get_roots(curr_user: models.User = Depends(get_current_active_user)):
    share_path = get_settings().SHARED_PATH.name
    home_path = str(Path(get_settings().HOMES_PATH.name)\
        .joinpath(curr_user.username))
    return Roots(shared=share_path, home=home_path)
