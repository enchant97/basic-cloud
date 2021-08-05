import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, Union
from uuid import UUID, uuid4

from fastapi import WebSocket

from .constants import (ContentChangeTypes, WebsocketMessageTypeReceive,
                        WebsocketMessageTypeSend)


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
        curr_dir = WebsocketHandler._clients_by_ws.get(client_uuid)
        if curr_dir:
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


@dataclass
class PayloadClientDirectoryChange:
    directory: Path


@dataclass
class PayloadServerDirectoryUpdate:
    path: Path
    change_type: ContentChangeTypes


@dataclass
class WebsocketMessage:
    message_type: Union[
        WebsocketMessageTypeSend,
        WebsocketMessageTypeReceive
    ]
    when: datetime
    payload: Union[
        PayloadClientDirectoryChange,
        PayloadServerDirectoryUpdate
    ]

    @classmethod
    def from_dict(cls, message: dict):
        msg_type = message["message_type"]
        when = message.get("when")
        if when:
            # XXX this will not work with js iso e.g 2021-07-30T15:29:50.175Z
            when = datetime.fromisoformat(message["when"])
        else:
            # has not provided a date
            when = datetime.utcnow()
        payload = message["payload"]
        if msg_type == WebsocketMessageTypeReceive.DIRECTORY_CHANGE:
            payload = PayloadClientDirectoryChange(Path(payload["directory"]))
        elif msg_type == WebsocketMessageTypeSend.WATCHDOG_UPDATE:
            payload = PayloadServerDirectoryUpdate(**payload)
        return cls(msg_type, when, payload)


async def dispatch_content_change(
        path: Path,
        change_type: ContentChangeTypes):
    message = WebsocketMessage(
        message_type=WebsocketMessageTypeSend.WATCHDOG_UPDATE,
        when=datetime.utcnow(),
        payload=PayloadServerDirectoryUpdate(
            path,
            change_type,
        ),
    )
    # TODO use custom json dump method
    message_str = json.dumps(asdict(message), default=str)

    # notify every path 'section'
    while path != Path():
        await WebsocketHandler.broadcast(message_str, path)
        path = path.parent
