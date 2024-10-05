from fastapi import FastAPI
from lecture_2.hw.shop_api.items_routes import router as item_router
from lecture_2.hw.shop_api.carts_routes import router as cart_router

app = FastAPI(title="Shop API")

app.include_router(item_router)
app.include_router(cart_router)