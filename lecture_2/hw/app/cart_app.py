from http import HTTPStatus
import logging
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import NonNegativeInt, PositiveInt
from responce.contract import *
from models.cart import *
from store.queries import *


cart_router = APIRouter(prefix="/cart")

@cart_router.get(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested cart",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested cart as one was not found",
        },
    },
)
async def get_item_cart(id: int) -> CartResponce:
    cart = get(id, 1)
    if cart is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Cart with id {id} didn't found",
        )
    return CartResponce.from_cart(cart)

@cart_router.get("")
async def get_list(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_quantity: Optional[int] = None,
    max_quantity: Optional[int] = None
) -> list[CartResponce]:
    if (min_price is not None and min_price < 0) or (max_price is not None and max_price < 0) \
    or (offset is not None and offset < 0) or (limit is not None and limit <= 0) \
    or (min_quantity is not None and min_quantity < 0) or (max_quantity is not None and max_quantity < 0)   :
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="all values must have non-negative values"
        )
    
    return [
        CartResponce.from_cart(e)
        for e in filter_carts(carts, offset, limit, min_price, max_price, min_quantity, max_quantity)
    ]

@cart_router.post(
    "",
    status_code=HTTPStatus.CREATED,
)
async def post_item(response: Response) -> dict:
    new_cart: Cart = add(carts)
    response.headers["location"] = f"/cart/{new_cart.id}"
    return {"id": new_cart.id}


@cart_router.post(
    "/{cart_id}/add/{item_id}",
        responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested cart",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested cart as one was not found",
        },
    },
)
async def add_item(item_id: int, cart_id: int) -> CartResponce:
    cart = add_item_to_cart(item_id, cart_id) 
    if cart is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Cart with id {id} not found",
        )
    return CartResponce.from_cart(cart)