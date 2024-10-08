from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import NonNegativeInt, PositiveInt, PositiveFloat

from lecture_2.hw.shop_api.api.shop.cart.contracts import CartResponse
from lecture_2.hw.shop_api.store import cart_store


cart_router = APIRouter(prefix="/cart")


@cart_router.post(
    "/",
    status_code=HTTPStatus.CREATED,
)
async def create_cart(response: Response) -> dict[str, int]:
    id_ = cart_store.add()
    response.headers["Location"] = f"/cart/{id_}"
    return {"id": id_}


@cart_router.post(
    "/{cart_id}/add/{item_id}",
    status_code=HTTPStatus.CREATED,
)
async def add_item_to_cart(cart_id: int, item_id: int) -> None:
    result = cart_store.add_item(cart_id, item_id)

    if result is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")

    return


@cart_router.get("/")
async def get_carts_list(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: Annotated[PositiveFloat, Query()] = None,
    max_price: Annotated[PositiveFloat, Query()] = None,
    min_quantity: Annotated[NonNegativeInt, Query()] = None,
    max_quantity: Annotated[NonNegativeInt, Query()] = None,
) -> list[CartResponse]:
    return [
        CartResponse.from_entity(entity)
        for entity in cart_store.get_many(
            offset, limit, min_price, max_price, min_quantity, max_quantity
        )
    ]


@cart_router.get(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested Cart",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested Cart as one was not found",
        },
    },
)
async def get_cart_by_id(id: int) -> CartResponse:
    entity = cart_store.get_one(id)
    print(entity)
    if entity is None:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /cart/{id} was not found",
        )

    return CartResponse.from_entity(entity)
