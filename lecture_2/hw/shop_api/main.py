from fastapi import FastAPI
from .routes import router
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Shop API")
Instrumentator().instrument(app).expose(app)
app.include_router(router)