from basic_cloud.config import get_settings
from basic_cloud.helpers.paths import create_root_path
from fastapi import (APIRouter, HTTPException, WebSocket, WebSocketDisconnect,
                     status)

from ..helpers.auth import get_current_user
from ..helpers.constants import WebsocketMessageTypeReceive
from ..helpers.exceptions import PathNotExists
from ..helpers.websocket import WebsocketHandler, WebsocketMessage

router = APIRouter()

@router.websocket("/ws")
async def watchdog_ws(
        websocket: WebSocket,
        bearer_token: str):
    client_uuid = None

    try:
        curr_user = await get_current_user(bearer_token)
        client_uuid = await WebsocketHandler.connect(websocket)
        while True:
            try:
                data = await websocket.receive_json()
                message = WebsocketMessage.from_dict(data)
                if message.message_type == WebsocketMessageTypeReceive.DIRECTORY_CHANGE:
                    real_path = create_root_path(
                        message.payload.directory,
                        get_settings().HOMES_PATH,
                        get_settings().SHARED_PATH,
                        curr_user.username,
                    )
                    if not real_path.exists() and not real_path.is_dir():
                        raise PathNotExists()

                    WebsocketHandler.move(client_uuid, message.payload.directory)

            except (ValueError, KeyError):
                # TODO handle this better
                print("invalid ws message received")

            except PathNotExists:
                # TODO handle this better
                raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    except HTTPException:
        # TODO remove this, and use WebSocketException when PR #527 on starlette is implemented
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    except WebSocketDisconnect:
        # we are handling this in finally
        pass

    finally:
        if client_uuid:
            WebsocketHandler.disconnect(client_uuid)
