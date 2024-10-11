from fastapi import FastAPI
from .routers import items, carts

app = FastAPI()

app.include_router(items.router)
app.include_router(carts.router)
