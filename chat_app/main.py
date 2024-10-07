from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Tuple

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
        username = None
        if chat_name not in self.active_connections:
            self.active_connections[chat_name] = []
        self.active_connections[chat_name].append((websocket, username))

    def set_username(self, chat_name: str, websocket: WebSocket, username: str):
        if chat_name in self.active_connections:
            for index, (ws, usr) in enumerate(self.active_connections[chat_name]):
                if ws == websocket:
                    self.active_connections[chat_name][index] = (ws, username)
                    break

    def disconnect(self, chat_name: str, websocket: WebSocket):
        if chat_name in self.active_connections:
            self.active_connections[chat_name] = [
                (ws, usr)
                for (ws, usr) in self.active_connections[chat_name]
                if ws != websocket
            ]
            if not self.active_connections[chat_name]:
                del self.active_connections[chat_name]

    async def broadcast(self, chat_name: str, message: str):
        if chat_name in self.active_connections:
            for connection, _ in self.active_connections[chat_name]:
                await connection.send_text(message)

    def get_username(self, chat_name: str, websocket: WebSocket):
        if chat_name in self.active_connections:
            for ws, username in self.active_connections[chat_name]:
                if ws == websocket:
                    return username
        return None


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


@app.get("/chat_rooms")
def list_chat_rooms():
    return {"chat_rooms": list(manager.chat_rooms.keys())}


@app.websocket("/chat/{chat_name}")
async def chat_endpoint(websocket: WebSocket, chat_name: str):
    await manager.connect(chat_name, websocket)
    try:
        data = await websocket.receive_text()
        if data.startswith("/username "):
            username = data.split(" ", 1)[1]
            manager.set_username(chat_name, websocket, username)
            await manager.broadcast(
                chat_name, f"*** {username} has joined the chat ***"
            )
        else:
            await websocket.close(code=1000)
            return

        while True:
            data = await websocket.receive_text()
            if data.strip() == "":
                continue  
            username = manager.get_username(chat_name, websocket)
            message = f"{username}: {data}"
            await manager.broadcast(chat_name, message)
    except WebSocketDisconnect:
        username = manager.get_username(chat_name, websocket)
        manager.disconnect(chat_name, websocket)
        await manager.broadcast(chat_name, f"*** {username} has left the chat ***")
    except Exception as e:
        await websocket.close(code=1000)
        print(f"Error: {e}")
