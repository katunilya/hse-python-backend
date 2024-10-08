from fastapi import FastAPI
from routers.item import router as item_router
from routers.cart import router as cart_router

app = FastAPI(title="Shop API")
app.include_router(item_router)
app.include_router(cart_router)

