from lecture_2.hw.shop_api.src.chats.storage import ConnectionsStorage

class ChatManager:
    def __init__(self, storage: ConnectionsStorage):
        self.storage = storage
        
    async def broadcast(self, message: str, chat_id: str):
        for connection in self.storage.connections[chat_id]:
            await connection.send_text(message)