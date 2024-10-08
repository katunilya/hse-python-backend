from fastapi import APIRouter, HTTPException, Response
from http import HTTPStatus
from lecture_2.hw.shop_api.store import queries
from lecture_2.hw.shop_api.api.cart.contracts import CartResponse

router = APIRouter(prefix="/cart")


@router.post("/", status_code=HTTPStatus.CREATED, response_model=CartResponse)
async def create_cart(response: Response):
    cart = queries.create_cart()
    response.headers["location"] = f"/cart/{cart.id}"
    return cart


@router.get("/{cart_id}", response_model=CartResponse)
async def get_cart(cart_id: int):
    cart = queries.get_cart(cart_id)
    if cart is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")
    return cart


@router.get("/", response_model=list)
async def get_cart_list(min_price: float = None, max_price: float = None, offset: int = 0, limit: int = 10):
    if offset < 0 or limit <= 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid pagination")

    carts = queries.get_carts(offset, limit, min_price, max_price)
    return carts


@router.post("/{cart_id}/add/{item_id}", response_model=CartResponse)
async def add_item_to_cart(cart_id: int, item_id: int):
    cart = queries.add_item_to_cart(cart_id, item_id)
    if not cart:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item or cart not found")
    return cart