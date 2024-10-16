
from fastapi import FastAPI
import logging
from app.item_app import item_router
from app.cart_app import cart_router

logging.basicConfig(level=logging.INFO)

def create_application():
    app = FastAPI()
    app.include_router(item_router)
    app.include_router(cart_router)
    return app

application = create_application()

