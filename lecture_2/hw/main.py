import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from shop_api.database.database import Base, engine
from shop_api.routes import routes

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

Base.metadata.create_all(bind=engine)
Instrumentator().instrument(app).expose(app)

app.include_router(routes.router)