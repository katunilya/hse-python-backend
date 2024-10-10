from fastapi import FastAPI
from app.routers import item, cart, chat

   app = FastAPI()
   app.include_router(item.router)
   app.include_router(cart.router)
   app.include_router(chat.router)