from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set, Tuple
import random
import string
from app.utils.connection_manager import ConnectionManager

   router = APIRouter()
   manager = ConnectionManager()

   @router.websocket("/chat/{chat_name}")
   async def websocket_endpoint(websocket: WebSocket, chat_name: str):
       username = await manager.connect(chat_name, websocket)
       try:
           while True:
               data = await websocket.receive_text()

               await manager.broadcast(chat_name, data, websocket)
       except WebSocketDisconnect:
           manager.disconnect(chat_name, websocket)