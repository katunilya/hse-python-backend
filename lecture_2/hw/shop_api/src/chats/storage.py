from typing import List

from fastapi import WebSocket

class ConnectionsStorage:
    def __init__(self):
        self.connections: dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: str):
        await websocket.accept()
        if chat_id not in self.connections:
            self.connections[chat_id] = []
        self.connections[chat_id].append(websocket)

    def disconnect(self, websocket: WebSocket, chat_id: str):
        self.connections[chat_id].remove(websocket)
        if not self.connections[chat_id]:
            del self.connections[chat_id]
