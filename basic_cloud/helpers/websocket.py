from collections import defaultdict
from pathlib import Path
from typing import Dict, Set

from fastapi import WebSocket


class WatchDogWsHandler:
    def __init__(self):
        self.__clients_by_dir: Dict[str, Set[WebSocket]] = defaultdict(set)
        self.__clients_by_ws: Dict[WebSocket: str] = {}

    async def connect(self, websocket: WebSocket, curr_dir: Path):
        await websocket.accept()
        curr_dir = str(curr_dir)
        self.__clients_by_dir[curr_dir].add(websocket)
        self.__clients_by_ws[websocket] = curr_dir

    def disconnect(self, websocket: WebSocket):
        curr_dir = self.__clients_by_ws.pop(websocket, None)
        if curr_dir is not None:
            self.__clients_by_dir[curr_dir].remove(websocket)

    async def __broadcast_dir(self, data: str, curr_dir: Path):
        curr_dir = str(curr_dir)
        for websocket in self.__clients_by_dir[curr_dir]:
            await websocket.send_text(data)

    async def __broadcast_all(self, data: str):
        for websocket in self.__clients_by_ws:
            await websocket.send_text(data)

    async def broadcast(self, data: str, curr_dir: Path = None):
        if curr_dir is None:
            await self.__broadcast_all(data)
        else:
            await self.__broadcast_dir(data, curr_dir)

    @property
    def conn_count(self) -> int:
        return len(self.__clients_by_ws)


# TODO add message creation helpers
