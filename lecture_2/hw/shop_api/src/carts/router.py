from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, HTTPException, Response, Query

from pydantic import NonNegativeInt, PositiveInt, PositiveFloat

from lecture_2.hw.shop_api.src.carts.schema import Cart, CartItem
from lecture_2.hw.shop_api.utils import generate_id
from lecture_2.hw.shop_api.storage import carts, items

cart_router = APIRouter()

@cart_router.post("/", status_code=HTTPStatus.CREATED)
def create_cart(response: Response):
    cart_id = generate_id()
    carts[cart_id] = Cart(id=cart_id)
    response.headers['location'] = f"/cart/{cart_id}"
    return {'id': cart_id}


@cart_router.get("/{id}")
def get_cart(id: int):
    cart = carts.get(id)
    if not cart:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")
    return cart


@cart_router.get("/")
def get_carts(
    offset: Annotated[NonNegativeInt, Query()] = 0, 
    limit: Annotated[PositiveInt, Query()] = 10, 
    min_price: Annotated[PositiveFloat, Query()] = None, 
    max_price: Annotated[PositiveFloat, Query()] = None, 
    min_quantity: Annotated[NonNegativeInt, Query()] = None, 
    max_quantity: Annotated[NonNegativeInt, Query()] = None 
):
    result = [
        cart for cart in carts.values()
        if (min_price is None or cart.price >= min_price)
        and (max_price is None or cart.price <= max_price)
        and (min_quantity is None or sum(item.quantity for item in cart.items) >= min_quantity)
        and (max_quantity is None or sum(item.quantity for item in cart.items) <= max_quantity)
    ]
    return result[offset:offset+limit]


@cart_router.post("/{cart_id}/add/{item_id}")
def add_item_to_cart(cart_id: int, item_id: int):
    cart = carts.get(cart_id)
    item = items.get(item_id)

    if not cart:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")
    
    if not item or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            break
    else:
        cart.items.append(CartItem(id=item_id, name=item.name, quantity=1, available=not item.deleted))

    cart.price = sum(item.quantity * items[item.id].price for item in cart.items)
