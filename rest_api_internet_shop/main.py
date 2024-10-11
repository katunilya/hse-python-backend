from fastapi import FastAPI

from routers import item, cart
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

Instrumentator().instrument(app).expose(app)

app.include_router(item.router, prefix="/item", tags=["Item"])
app.include_router(cart.router, prefix="/cart", tags=["Cart"])
