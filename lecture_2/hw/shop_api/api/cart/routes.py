import sys
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import NonNegativeInt, PositiveInt

from .contracts import CartResponse

from lecture_2.hw.shop_api import store
from ...store.models import CartEntity

router = APIRouter(prefix="/cart")


@router.post("/", status_code=HTTPStatus.CREATED)
async def post_cart(response: Response) -> CartEntity:
    entity = store.create_cart()
    response.headers["location"] = f"/cart/{entity.id}"
    return entity


@router.get(
    "/{id}",
    responses={
        HTTPStatus.OK: {"description": "Successfully returned requested cart"},
        HTTPStatus.NOT_FOUND: {"description": "Failed to return requested cart as one was not found"}})
async def get_cart_by_id(id: int):
    entity = store.get_cart_by_id(id)
    if not entity:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /cart/{id} was not found",
        )
    return entity


@router.get("/")
async def get_cart_list(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: float = Query(0, ge=0),
    max_price: float = Query(sys.maxsize, ge=0),
    min_quantity: int = Query(0, ge=0),
    max_quantity: int = Query(sys.maxsize, ge=0),
) -> list[CartResponse]:
    return [CartResponse.from_entity(e) for e in store.get_many_carts(offset, limit, min_price, max_price, min_quantity, max_quantity)]


@router.post("/{cart_id}/add/{item_id}",
             responses={
             HTTPStatus.OK: {"description": "Successfully added"},
             HTTPStatus.NOT_FOUND: {"description": "Failed to return requested pokemon as one was not found"}})
async def add_item_to_cart(cart_id: int, item_id: int):
    store.add_item_to_cart(cart_id, item_id)



