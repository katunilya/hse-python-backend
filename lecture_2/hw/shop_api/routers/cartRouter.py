from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import NonNegativeInt, PositiveInt, PositiveFloat

from lecture_2.hw.shop_api.db.queries import *

cartRouter = APIRouter(prefix="/cart")


@cartRouter.post("/")
def cartCreateItem():
    id = createNewCartInCarts()
    return JSONResponse(content={"id": id}, status_code=HTTPStatus.CREATED, headers={"location": f"/cart/{id}"})


@cartRouter.get("/{id}")
def getById(id: int):
    return getCartById(id)


@cartRouter.post("/{cart_id}/add/{item_id}")
def postItem(cart_id: int, item_id: int):
    return addItemToCart(cart_id, item_id)


@cartRouter.get("/")
def getCarts(offset: NonNegativeInt = 0, limit: PositiveInt = 10, min_price: PositiveFloat = None,
             max_price: PositiveFloat = None, min_quantity: NonNegativeInt = None, max_quantity: NonNegativeInt = None):
    return getCartList(offset, limit, min_price, max_price, min_quantity, max_quantity)
