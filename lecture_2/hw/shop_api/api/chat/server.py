import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import random

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_name: str):
        await websocket.accept()
        if chat_name not in self.active_connections:
            self.active_connections[chat_name] = []
        self.active_connections[chat_name].append(websocket)

    def disconnect(self, websocket: WebSocket, chat_name: str):
        self.active_connections[chat_name].remove(websocket)
        if not self.active_connections[chat_name]:
            del self.active_connections[chat_name]

    async def broadcast(self, message: str, chat_name: str):
        for connection in self.active_connections[chat_name]:
            await connection.send_text(message)


manager = ConnectionManager()

@app.websocket("/chat/{chat_name}")
async def websocket_endpoint(websocket: WebSocket, chat_name: str):
    username = f"user_{random.randint(1000, 9999)}"
    await manager.connect(websocket, chat_name)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = f"{username} :: {data}"
            await manager.broadcast(message, chat_name)
    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_name)
        await manager.broadcast(f"{username} покинул чат(((.", chat_name)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
