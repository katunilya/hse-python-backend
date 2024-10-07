from fastapi import FastAPI, Depends
from lecture_2.hw.shop_api.app.carts import router as carts_router 
from lecture_2.hw.shop_api.app.items import router as items_router
from lecture_2.hw.shop_api.app.counter import CounterService

app = FastAPI(title="Shop API")

counter_service = CounterService()

def get_counter_service():
    return counter_service

app.include_router(items_router, dependencies=[Depends(get_counter_service)])
app.include_router(carts_router, dependencies=[Depends(get_counter_service)])