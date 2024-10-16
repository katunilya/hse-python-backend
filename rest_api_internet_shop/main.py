from fastapi import FastAPI

from rest_api_internet_shop.routers import item, cart

app = FastAPI()

app.include_router(item.router, prefix="/item", tags=["Item"])
app.include_router(cart.router, prefix="/cart", tags=["Cart"])
