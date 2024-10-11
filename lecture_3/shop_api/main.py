from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from .api.routes import cart_router, item_router



app = FastAPI(title="Shop API")

Instrumentator().instrument(app).expose(app)

app.include_router(cart_router)
app.include_router(item_router)
