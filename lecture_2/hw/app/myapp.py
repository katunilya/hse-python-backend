
from fastapi import FastAPI
import logging
from .item_app import item_router
from .cart_app import cart_router



logging.basicConfig(level=logging.INFO)

def create_application():
    app = FastAPI()
    app.include_router(item_router)
    app.include_router(cart_router)
    return app

application = create_application()

