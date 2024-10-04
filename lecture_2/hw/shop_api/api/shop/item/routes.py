from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import NonNegativeInt, PositiveInt, PositiveFloat

from lecture_2.hw.shop_api.api.shop.item.contracts import (
    ItemRequest,
    ItemResponse,
    PatchItemRequest,
)
from lecture_2.hw.shop_api.store import item_store


item_router = APIRouter(prefix="/item")


@item_router.post(
    "/",
    status_code=HTTPStatus.CREATED,
)
async def post_item(item: ItemRequest, response: Response) -> ItemResponse:

    entity = item_store.add(item.as_item_info())
    response.headers["location"] = f"/item/{entity.id_}"
    return ItemResponse.from_entity(entity)


@item_router.get("/")
async def get_items_list(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: Annotated[PositiveFloat, Query()] = None,
    max_price: Annotated[PositiveFloat, Query()] = None,
    show_deleted: Annotated[bool, Query()] = False,
) -> list[ItemResponse]:
    return [
        ItemResponse.from_entity(entity)
        for entity in item_store.get_many(
            offset, limit, min_price, max_price, show_deleted
        )
    ]


@item_router.get(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested Item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested Item as one was not found",
        },
    },
)
async def get_item_by_id(id: int) -> ItemResponse:
    entity = item_store.get_one(id)

    if entity is None:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /item/{id} was not found",
        )

    return ItemResponse.from_entity(entity)


@item_router.put(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully updated Item",
        },
        HTTPStatus.NOT_MODIFIED: {
            "description": "Failed to modify Item as one was not found",
        },
    },
)
async def put_item(id: int, info: ItemRequest) -> ItemResponse:
    entity = item_store.update(id, info.as_item_info())

    if entity is None:
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            f"Requested resource /item/{id} was not found",
        )

    return ItemResponse.from_entity(entity)


@item_router.patch(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully patched Item",
        },
        HTTPStatus.NOT_MODIFIED: {
            "description": "Failed to modify Item as one was not found",
        },
    },
)
async def patch_item(id: int, info: PatchItemRequest) -> ItemResponse:
    entity = item_store.patch(id, info.as_patch_item_info())

    if entity is None:
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            f"Requested resource /item/{id} was not found",
        )

    return ItemResponse.from_entity(entity)


@item_router.delete("/{id}")
async def delete_item(id: int) -> ItemResponse:
    item_store.delete(id)

    return Response("")
