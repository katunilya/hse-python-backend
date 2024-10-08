from fastapi import FastAPI

from shop_api.api.shop.item.routes import item_router
from shop_api.api.shop.cart.routes import cart_router
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Shop API")
app.include_router(item_router)
app.include_router(cart_router)
Instrumentator().instrument(app).expose(app)
