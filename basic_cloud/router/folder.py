import base64
import binascii
import shutil
from pathlib import Path
from typing import List

from fastapi import (APIRouter, Body, Depends, HTTPException, WebSocket,
                     WebSocketDisconnect, status)
from fastapi.responses import PlainTextResponse, StreamingResponse

from ..config import get_settings
from ..database import crud, models, schema
from ..helpers.auth import get_current_active_user, get_current_user
from ..helpers.constants import ContentChangeTypes
from ..helpers.exceptions import PathNotExists
from ..helpers.paths import (create_root_path, create_zip, is_root_path,
                             relative_dir_contents)
from ..helpers.schema import PathContent, Roots
from ..shared import watchdog_ws_handler

router = APIRouter()


@router.get(
    "",
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
    "",
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
    if get_settings().HISTORY_LOG:
        await crud.create_content_change(
            directory,
            ContentChangeTypes.CREATION,
            True,
            curr_user,
        )
    return directory


@router.get(
    "/{directory}/contents",
    response_model=List[PathContent],
    description="get a specific directory content")
async def get_directory_contents(
        directory: str,
        curr_user: models.User = Depends(get_current_active_user)):
    try:
        root_path = Path(base64.b64decode(directory).decode())
        root_path = create_root_path(
            root_path,
            get_settings().HOMES_PATH,
            get_settings().SHARED_PATH,
            curr_user.username,
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
    except PathNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unknown root directory",
        )
    except (ValueError, binascii.Error):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="malformed base64 filename"
        ) from None



@router.get(
    "/{directory}/history",
    response_model=List[schema.ContentChange],
    description="get history for folder")
async def get_history_by_folder(
        directory: str,
        curr_user: models.User = Depends(get_current_active_user)):
    try:
        directory = Path(base64.b64decode(directory).decode())
        full_path = create_root_path(
            directory,
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
        return await crud.get_content_changes_by_path(directory)

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
    "/{directory}/download",
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
        if get_settings().HISTORY_LOG:
            await crud.create_content_change(
                directory,
                ContentChangeTypes.DOWNLOAD,
                True,
                curr_user,
            )
        return StreamingResponse(zip_obj, media_type="application/zip")

    except PathNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unknown root directory",
        )

    except (ValueError, binascii.Error):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="malformed base64 filename"
        ) from None


@router.delete(
    "/{directory}",
    description="delete a directory")
async def delete_directory(
        directory: str,
        curr_user: models.User = Depends(get_current_active_user)):
    try:
        full_path = Path(base64.b64decode(directory).decode())
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
        if get_settings().HISTORY_LOG:
            await crud.create_content_change(
                directory,
                ContentChangeTypes.DELETION,
                True,
                curr_user,
            )

    except PathNotExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unknown root directory",
        )
    except (ValueError, binascii.Error):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="malformed base64 filename"
        ) from None


@router.websocket("/{directory}/watchdog-ws/{bearer_token}")
async def watchdog_ws(
        websocket: WebSocket,
        directory: str,
        bearer_token: str):

    try:
        curr_user = await get_current_active_user(await get_current_user(bearer_token))
        directory = base64.b64decode(directory).decode()
        directory = Path(directory)
        try:
            real_path = create_root_path(
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

        if not real_path.exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="directory must exist",
            )
        if not real_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="path must be a directory",
            )
        await watchdog_ws_handler.connect(websocket, directory)

    except HTTPException:
        # TODO remove this, and use WebSocketException when PR #527 on starlette is implemented
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    except WebSocketDisconnect:
        watchdog_ws_handler.disconnect(websocket)
