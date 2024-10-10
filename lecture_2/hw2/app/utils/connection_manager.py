from typing import Dict, Set, Tuple
from threading import Lock
import random
import string
from fastapi import WebSocket

   class ConnectionManager:
       def __init__(self):
           self.active_connections: Dict[str, Set[Tuple[WebSocket, str]]] = {}
           self.lock = Lock()

       async def connect(self, chat_name: str, websocket: WebSocket):
           await websocket.accept()
           username = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
           with self.lock:
               if chat_name not in self.active_connections:
                   self.active_connections[chat_name] = set()
               self.active_connections[chat_name].add((websocket, username))
           return username

       def disconnect(self, chat_name: str, websocket: WebSocket):
           with self.lock:
               if chat_name in self.active_connections:
                   connection_to_remove = None
                   for conn in self.active_connections[chat_name]:
                       if conn[0] == websocket:
                           connection_to_remove = conn
                           break
                   if connection_to_remove:
self.active_connections[chat_name].remove(connection_to_remove)
                   if not self.active_connections[chat_name]:
                       del self.active_connections[chat_name]

       async def broadcast(self, chat_name: str, message: str, sender_websocket: WebSocket):
           with self.lock:
               if chat_name in self.active_connections:
                   sender_username = None
                   for conn in self.active_connections[chat_name]:
                       if conn[0] == sender_websocket:
                           sender_username = conn[1]
                           break
                   if sender_username is None:
                       return
                   for conn in self.active_connections[chat_name]:
                       websocket, username = conn
                       if websocket != sender_websocket:
                           await websocket.send_text(f"{sender_username} :: {message}")