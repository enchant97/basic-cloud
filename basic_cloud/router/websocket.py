from fastapi import (APIRouter, HTTPException, WebSocket, WebSocketDisconnect,
                     status)

from ..helpers.auth import get_current_user
from ..helpers.websocket import WebsocketHandler

router = APIRouter()

@router.websocket("/ws")
async def watchdog_ws(
        websocket: WebSocket,
        bearer_token: str):
    client_uuid = None

    try:
        curr_user = await get_current_user(bearer_token)
        print(curr_user)
        client_uuid = await WebsocketHandler.connect(websocket)
        while True:
            data = await websocket.receive_json()
            print("recieved ws data:", data)

    except HTTPException:
        # TODO remove this, and use WebSocketException when PR #527 on starlette is implemented
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

    except WebSocketDisconnect:
        if client_uuid:
            WebsocketHandler.disconnect(client_uuid)
        print(WebsocketHandler.get_conn_count())
