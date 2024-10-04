from fastapi import FastAPI

from lecture_2.hw.shop_api.api.shop.item.routes import item_router
from lecture_2.hw.shop_api.api.shop.cart.routes import cart_router

app = FastAPI(title="Shop API")

app.include_router(item_router)
app.include_router(cart_router)
