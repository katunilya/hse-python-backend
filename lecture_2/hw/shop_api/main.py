from fastapi import FastAPI

from lecture_2.hw.shop_api.src.carts.router import cart_router
from lecture_2.hw.shop_api.src.items.router import item_router

app = FastAPI(title="Shop API")
app.include_router(cart_router, prefix="/cart")
app.include_router(item_router, prefix="/item")