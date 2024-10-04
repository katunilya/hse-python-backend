from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import NonNegativeFloat, NonNegativeInt, PositiveInt

from lecture_2.hw.shop_api.api.contracts import (
    CartResponse,
    ItemRequest,
    ItemResponse,
    PatchItemRequest,
)
from lecture_2.hw.shop_api import store


item_router = APIRouter(prefix="/item")
cart_router = APIRouter(prefix="/cart")


@item_router.post(
    "/",
    status_code=HTTPStatus.CREATED,
)
async def post_item(info: ItemRequest, response: Response) -> ItemResponse:
    entity = store.add_item(info.as_item_info())

    # as REST states one should provide uri to newly created resource in location header
    response.headers["location"] = f"/item/{entity.id}"

    return ItemResponse.from_entity(entity)


@cart_router.post(
    "/",
    status_code=HTTPStatus.CREATED,
)
async def post_cart(response: Response) -> CartResponse:
    entity = store.add_cart()

    # as REST states one should provide uri to newly created resource in location header
    response.headers["location"] = f"/cart/{entity.id}"

    return CartResponse.from_entity(entity)


@item_router.get(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested item as one was not found",
        },
    },
)
async def get_item_by_id(id: int) -> ItemResponse:
    entity = store.get_item(id)

    if not entity:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /item/{id} was not found",
        )

    return ItemResponse.from_entity(entity)


@cart_router.get(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested item as one was not found",
        },
    },
)
async def get_cart_by_id(id: int) -> CartResponse:
    entity = store.get_cart(id)

    if not entity:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /item/{id} was not found",
        )

    return CartResponse.from_entity(entity)


@cart_router.get("/")
async def get_cart_list(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: Annotated[NonNegativeFloat, Query()] = None,
    max_price: Annotated[NonNegativeFloat, Query()] = None,
    min_quantity: Annotated[NonNegativeInt, Query()] = None,
    max_quantity: Annotated[NonNegativeInt, Query()] = None,
) -> list[CartResponse]:
    return [
        CartResponse.from_entity(e)
        for e in store.get_many_carts(
            offset, limit, min_price, max_price, min_quantity, max_quantity
        )
    ]


@item_router.delete("/{id}")
async def delete_item(id: int) -> Response:
    store.delete_item(id)
    return Response("")


@item_router.put("/{id}")
async def put_item(id: int, info: ItemRequest) -> ItemResponse:
    entity = store.update_item(id, info.as_item_info())

    if entity is None:
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            f"Requested resource /item/{id} was not found",
        )

    return ItemResponse.from_entity(entity)


@item_router.get("/")
async def get_item_list(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: Annotated[NonNegativeFloat, Query()] = None,
    max_price: Annotated[NonNegativeFloat, Query()] = None,
    show_deleted: Annotated[bool, Query()] = False,
) -> list[ItemResponse]:
    return [
        ItemResponse.from_entity(e)
        for e in store.get_many_items(offset, limit, min_price, max_price, show_deleted)
    ]


@item_router.patch(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully patched item",
        },
        HTTPStatus.NOT_MODIFIED: {
            "description": "Failed to modify item as one was not found",
        },
    },
)
async def patch_item(id: int, info: PatchItemRequest) -> ItemResponse:
    entity = store.patch_item(id, info.as_patch_item_info())

    if entity is None:
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            f"Requested resource /item/{id} was not found",
        )

    return ItemResponse.from_entity(entity)


@cart_router.post(
    "/{cart_id}/add/{item_id}",
    status_code=HTTPStatus.CREATED,
)
async def post_add_item_to_cart(cart_id: int, item_id: int) -> Response:
    store.add_item_to_cart(cart_id, item_id)

    return Response("")
