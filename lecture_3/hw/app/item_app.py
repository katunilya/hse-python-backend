from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import NonNegativeInt, PositiveInt
from responce.contract import *
from models.item import *
from store.queries import *

item_router = APIRouter(prefix="/item")


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
async def get_item_item(id: int) -> ItemResponce:
    item = get(id, 0)
    if item is None or item.item.deleted:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Item with id {id} not found or has been deleted",
        )
    return ItemResponce.from_item(item)


@item_router.post(
    "",
    status_code=HTTPStatus.CREATED,
)
async def post_item(item: ItemRequest, response: Response) -> ItemResponce:
    new_item: Item = add(items, item.as_item())
    response.headers["location"] = f"/item/{new_item.id}"
    return ItemResponce.from_item(new_item)


@item_router.delete("/{id}")
async def delete(id: int) -> Response:
    flag: bool = delete_item(id)
    if flag:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Item with id {id} not found or has been deleted",
        )
    return Response("")


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
async def patch_item_app(id: int, request_patch_item: PatchItemRequest):
    patched_item = request_patch_item.as_patch_item()
    out = patch_item(id, patched_item)
    if out is None:
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            f"Requested resource /item/{id} was not found",
        )
    return ItemResponce.from_item(out)


@item_router.put(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully updated or upserted pokemon",
        },
        HTTPStatus.NOT_MODIFIED: {
            "description": "Failed to modify pokemon as one was not found",
        },
    },
)
async def put_item(id: int, item: ItemRequest) -> ItemResponce:
    out = replace_item(id, item.as_item())
    if out is None:
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            f"Requested resource /item/{id} was not found",
        )
    return ItemResponce.from_item(out)


@item_router.get("")
async def get_list(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    show_deleted: bool = False,
) -> list[ItemResponce]:
    if (min_price is not None and min_price < 0) or (max_price is not None and max_price < 0):
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="all values must have non-negative values"
        )
    return [
        ItemResponce.from_item(e)
        for e in filter_items(items, offset, limit, min_price, max_price, show_deleted)
    ]
