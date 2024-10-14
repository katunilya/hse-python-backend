

from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from lecture_2.hw.shop_api.src.chats.manager import ChatManager
from lecture_2.hw.shop_api.src.chats.storage import ConnectionsStorage
from lecture_2.hw.shop_api.utils import generate_id

storage = ConnectionsStorage()
manager = ChatManager(storage=storage)

chat_router = APIRouter()

@chat_router.websocket("/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    username = f"user_{generate_id()}"
    await storage.connect(websocket, chat_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = f"{username}: {data}"
            await manager.broadcast(message, chat_id)

    except WebSocketDisconnect:
        storage.disconnect(websocket, chat_id)
        await manager.broadcast(f"{username} disconnected", chat_id)