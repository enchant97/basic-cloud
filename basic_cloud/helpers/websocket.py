from collections import defaultdict
from pathlib import Path
from typing import Dict, Set
from uuid import UUID, uuid4

from fastapi import WebSocket


class WebsocketHandler:
    """
    static class allowing for easy access to client websockets
    """
    _ws_by_uuid: Dict[UUID, WebSocket] = {}
    _clients_by_dir: Dict[str, Set[UUID]] = defaultdict(set)
    _clients_by_ws: Dict[UUID, str] = {}

    @staticmethod
    async def connect(websocket: WebSocket, curr_dir: Path = None):
        await websocket.accept()
        client_uuid = uuid4()
        WebsocketHandler._ws_by_uuid[client_uuid] = websocket

        if curr_dir is not None:
            curr_dir = str(curr_dir)
            WebsocketHandler._clients_by_dir[curr_dir].add(client_uuid)
            WebsocketHandler._clients_by_ws[client_uuid] = curr_dir
        return client_uuid

    @staticmethod
    def move(client_uuid: UUID, new_dir: Path):
        new_dir = str(new_dir)
        # remove client from current directory
        curr_dir = WebsocketHandler._clients_by_ws[client_uuid]
        WebsocketHandler._clients_by_dir[curr_dir].discard(client_uuid)
        # add to new directory
        WebsocketHandler._clients_by_dir[new_dir].add(client_uuid)

    @staticmethod
    def disconnect(client_uuid: UUID):
        curr_dir = WebsocketHandler._clients_by_ws.pop(client_uuid, None)
        WebsocketHandler._clients_by_dir[curr_dir].discard(client_uuid)
        del WebsocketHandler._ws_by_uuid[client_uuid]

    @staticmethod
    async def _broadcast_dir(data: str, curr_dir: Path):
        curr_dir = str(curr_dir)
        for client_uuid in WebsocketHandler._clients_by_dir[curr_dir]:
            client_ws = WebsocketHandler._ws_by_uuid[client_uuid]
            await client_ws.send_text(data)

    @staticmethod
    async def _broadcast_all(data: str):
        for client_uuid in WebsocketHandler._clients_by_ws:
            client_ws = WebsocketHandler._ws_by_uuid[client_uuid]
            await client_ws.send_text(data)

    @staticmethod
    async def broadcast(data: str, curr_dir: Path = None):
        if curr_dir is None:
            await WebsocketHandler._broadcast_all(data)
        else:
            await WebsocketHandler._broadcast_dir(data, curr_dir)

    @staticmethod
    def get_conn_count() -> int:
        return len(WebsocketHandler._ws_by_uuid)


# TODO add message creation helpers
