import sys
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response

from lecture_2.hw.shop_api import store
from .contracts import ItemRequest
from ...store.models import ItemEntity
from pydantic import NonNegativeInt, PositiveInt

router = APIRouter(prefix="/item")


@router.post("/", status_code=HTTPStatus.CREATED)
async def post_item(request: ItemRequest, response: Response) -> ItemEntity:
    entity = store.create_item(request.name, request.price)
    response.headers["location"] = f"/item/{entity.id}"
    return entity

@router.get(
    "/{id}",
    responses={
        HTTPStatus.OK: {"description": "Successfully returned requested item"},
        HTTPStatus.NOT_FOUND: {"description": "Failed to return requested item as one was not found"}})
async def get_item_by_id(id: int):
    entity = store.get_item_by_id(id)

    if not entity:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /item/{id} was not found",
        )
    return entity


@router.get("/")
async def get_item_list(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: float = Query(0, ge=0),
    max_price: float = Query(sys.maxsize, ge=0),
    show_deleted: bool = False,
) -> list[ItemEntity]:
    return [e for e in store.get_many_items(offset, limit, min_price, max_price, show_deleted)]


@router.put("/{id}")
def change_item(id: int, new_item: ItemRequest):
    return store.update_item(id, new_item.name, new_item.price)


@router.patch("/{id}")
def patch_item(id: int, new_item: ItemRequest):
    return store.patch_item(id, new_item.name, new_item.price)

@router.delete("/{id}")
def delete_item(id: int):
    return store.delete_item(id)