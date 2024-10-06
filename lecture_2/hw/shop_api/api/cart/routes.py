from http import HTTPStatus
from typing import Annotated, Optional

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import NonNegativeInt, PositiveInt

from .contracts import (
    CartResponse,
    CartRequest,
    PatchCartRequest,
)
from .entities import *
from .functions import *


router = APIRouter(prefix="/cart")


@router.post(
        "/",
        status_code=HTTPStatus.CREATED,
)
async def create_cart(response: Response, info: CartRequest = None) -> CartResponse:
    # Если info не передан, создаем пустую корзину
    if info is None:
        info = CartRequest(items=[], price=0.0)

    entity = add(info.as_cart_info())
    entity = update_cart_price(entity)
    response.headers["location"] = f"/cart/{entity.id}"
    return CartResponse.from_entity(entity)


@router.get(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested cart",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested cart as one was not found, unfortunate",
        },
    }
)
async def get_one(id: int) -> CartResponse:
    entity = get_one_cart(id)
    if not entity:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /cart/{id} was not found, unfortunate",
        )
    return CartResponse.from_entity(entity)


@router.get("/")
async def get_cart_list(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[NonNegativeInt, Query(gt=0)] = 10,
    min_price: float = Query(None, ge=0),
    max_price: float = Query(None, ge=0),
    min_quantity: int = Query(None, ge=0),
    max_quantity: int = Query(None, ge=0),
) -> List[CartResponse]:
    return[CartResponse.from_entity(e) for e in get_many(
        offset, limit, min_price, max_price, min_quantity, max_quantity,
    )]


@router.post(
    "/{cart_id}/add/{item_id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully put item in a cart",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "No such cart_id or item_id",
        },
    },
)
async def new_item_cart(cart_id: int, item_id: int) -> CartResponse:
    return CartResponse.from_entity(put_item_in_cart(cart_id, item_id))