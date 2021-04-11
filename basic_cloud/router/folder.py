from pathlib import Path
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, status

from ..config import get_settings
from ..database import models
from ..helpers.auth import get_current_active_user
from ..helpers.paths import PathContent, relative_dir_contents, Roots

router = APIRouter()


@router.post("/contents", response_model=List[PathContent])
async def get_directory_contents(
        directory: str = Body(..., embed=True),
        curr_user: models.User = Depends(get_current_active_user)):
    root_path = Path(directory)
    if root_path.parts[0] != "shared"\
            and root_path.parts[0:2] != ("homes", curr_user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unknown root directory",
        )
    parts = root_path.parts[1:]
    if root_path.parts[0] == "shared":
        # must be the shared directory
        if parts:
            root_path = get_settings().SHARED_PATH.joinpath(*parts)
        else:
            root_path = get_settings().SHARED_PATH
    else:
        # must be a user home directory
        if parts:
            root_path = get_settings().HOMES_PATH.joinpath(*parts)
        else:
            root_path = get_settings().HOMES_PATH

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
