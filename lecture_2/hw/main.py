# main.py

from fastapi import FastAPI
from shop_api.database.database import Base, engine
from shop_api.routes import routes

app = FastAPI()

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Подключение маршрутов
app.include_router(routes.router)
