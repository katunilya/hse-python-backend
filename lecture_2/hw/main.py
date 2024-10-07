import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from shop_api.database.database import Base, engine
from shop_api.routes import routes

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(routes.router)

#Hello
