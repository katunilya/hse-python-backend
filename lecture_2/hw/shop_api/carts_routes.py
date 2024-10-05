from typing import Annotated
from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import NonNegativeInt, PositiveInt, NonNegativeFloat

from lecture_2.hw.shop_api.contracts import (
    ItemRequest,
    ItemResponse,
    PatchItemRequest,
    PutItemRequest,
    CartResponse,
)
from lecture_2.hw.shop_api.models import ItemInfo, Item, PatchItemInfo, ItemInCart, Cart
import lecture_2.hw.shop_api.carts_queries as queries


router = APIRouter(prefix="/cart")


@router.post("/", status_code=HTTPStatus.CREATED)
async def post_cart(response: Response) -> dict:
    cart = queries.create_empty_cart()

    # as REST states one should provide uri to newly created resource in location header
    response.headers["location"] = f"/cart/{cart.id}"
    return {"id": cart.id}


@router.get("/{cart_id}", status_code=HTTPStatus.OK)
async def get_cart_by_id(cart_id: int) -> CartResponse:
    cart = queries.get_cart_by_id(cart_id)

    if cart == "cart not found":
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /cart/{cart_id} was not found",
        )
    return CartResponse.from_cart(cart)


@router.post("/{cart_id}/add/{item_id}", status_code=HTTPStatus.CREATED)
async def add_item_to_cart(cart_id: int, item_id: int) -> None:
    cart = queries.add_item_to_cart(cart_id, item_id)
    if cart == "cart not found":
        raise HTTPException(HTTPStatus.NOT_FOUND, f"Cart /cart/{cart_id} was not found")
    elif cart == "item not found":
        raise HTTPException(HTTPStatus.NOT_FOUND, f"Item /item/{item_id} was not found")


@router.get("/", status_code=HTTPStatus.OK)
async def get_cart_list(
    offset: Annotated[NonNegativeInt, Query(ge=0)] = 0,
    limit: Annotated[PositiveInt, Query(gt=0)] = 10,
    min_price: Annotated[NonNegativeFloat | None, Query(ge=0.0)] = None,
    max_price: Annotated[NonNegativeFloat | None, Query(ge=0.0)] = None,
    min_quantity: Annotated[NonNegativeInt | None, Query(ge=0)] = None,
    max_quantity: Annotated[NonNegativeInt | None, Query(ge=0)] = None,
) -> list[CartResponse]:
    if offset < 0 or limit < 0:
        raise HTTPException(
            HTTPStatus.UNPROCESSABLE_ENTITY, "Get parameters must be non-negatitve"
        )
    if (
        min_price is not None
        and min_price < 0
        or max_price is not None
        and max_price < 0
        or min_quantity is not None
        and min_quantity < 0
        or max_quantity is not None
        and max_quantity < 0
    ):
        raise HTTPException(
            HTTPStatus.UNPROCESSABLE_ENTITY, "Get parameters must be non-negatitve"
        )
    return [
        CartResponse.from_cart(cart)
        for cart in queries.get_many_carts(
            offset, limit, min_price, max_price, min_quantity, max_quantity
        )
    ]
