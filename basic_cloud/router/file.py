from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.responses import FileResponse

from ..config import get_settings
from ..database import models
from ..helpers.auth import get_current_active_user
from ..helpers.exceptions import PathNotExists
from ..helpers.paths import create_root_path

router = APIRouter()
download_tokens = dict()


@router.post("/download/new-token")
async def create_download_token(
        root_path: Path = Body(..., embed=True),
        curr_user: models.User = Depends(get_current_active_user)):
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

    if not root_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_401_BAD_REQUEST,
            detail="cannot be a directory",
        )

    dt_now = datetime.utcnow()

    # cleanup old tokens
    for key in download_tokens:
        if download_tokens[key]["expires"] < dt_now:
            del download_tokens[key]

    token = uuid4()
    expires = dt_now + timedelta(minutes=4)
    download_tokens[token] = {"path": root_path, "expires": expires}

    return {"token": str(token)}


@router.get("/download/by-token/{token}", response_class=FileResponse)
async def download_file_by_token(token: UUID):
    if token not in download_tokens:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # remove the token so it can't be used again
    token_contents = download_tokens.pop(token)

    if token_contents["expires"] < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )

    file_path = token_contents["path"]
    return FileResponse(file_path, filename=file_path.name)
