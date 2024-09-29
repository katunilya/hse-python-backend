from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
import uuid
from typing import Dict, List, Tuple
import asyncio

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[Tuple[WebSocket, str]]] = {}
        self.chat_rooms: Dict[str, bool] = {}

    def create_chat_room(self, chat_name: str):
        if chat_name in self.chat_rooms:
            raise ValueError("Chat room already exists")
        self.chat_rooms[chat_name] = True

    async def connect(self, chat_name: str, websocket: WebSocket):
        if chat_name not in self.chat_rooms:
            await websocket.close(code=1000)
            raise WebSocketDisconnect()
        await websocket.accept()
        username = str(uuid.uuid4())[:8]
        if chat_name not in self.active_connections:
            self.active_connections[chat_name] = []
        self.active_connections[chat_name].append((websocket, username))
        return username

    def disconnect(self, chat_name: str, websocket: WebSocket):
        if chat_name in self.active_connections:
            self.active_connections[chat_name] = [
                (ws, usr) for (ws, usr) in self.active_connections[chat_name]
                if ws != websocket
            ]
            if not self.active_connections[chat_name]:
                del self.active_connections[chat_name]

    async def broadcast(self, chat_name: str, message: str, sender_ws: WebSocket):
        if chat_name in self.active_connections:
            for (connection, _) in self.active_connections[chat_name]:
                if connection != sender_ws:
                    await connection.send_text(message)

manager = ConnectionManager()

class ChatRoom(BaseModel):
    name: str

@app.post("/chat_rooms")
def create_chat_room(chat_room: ChatRoom):
    try:
        manager.create_chat_room(chat_room.name)
        return {"message": f"Chat room '{chat_room.name}' created successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/chat/{chat_name}")
async def chat_endpoint(websocket: WebSocket, chat_name: str):
    try:
        username = await manager.connect(chat_name, websocket)
        try:
            while True:
                data = await websocket.receive_text()
                message = f"{username} :: {data}"
                await manager.broadcast(chat_name, message, websocket)
        except WebSocketDisconnect:
            manager.disconnect(chat_name, websocket)
    except WebSocketDisconnect:
        pass  
    except Exception as e:
        await websocket.close(code=1000)
        print(f"Error: {e}")

@app.get("/chat_rooms")
def list_chat_rooms():
    return {"chat_rooms": list(manager.chat_rooms.keys())}
