
from fastapi import FastAPI
from routers import shop_router
app = FastAPI()

app.include_router(shop_router)
#app.include_router(router = item_router)