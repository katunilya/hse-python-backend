from fastapi import FastAPI

from lecture_2.hw.shop_api.api.routes import cart_router, item_router

app = FastAPI(title="Shop API")

app.include_router(cart_router)
app.include_router(item_router)
