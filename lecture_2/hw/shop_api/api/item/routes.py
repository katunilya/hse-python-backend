from http import HTTPStatus
from typing import Annotated, Optional
import pprint 
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import NonNegativeInt, PositiveInt

from .contracts import (
    ItemResponse,
    ItemRequest,
    PatchItemRequest,
)

from .entities import *
from .functions import *


router = APIRouter(prefix="/item")


@router.post(
        "/",
        status_code=HTTPStatus.CREATED,
)
async def create_item(info: ItemRequest, response: Response) -> ItemResponse:
    entity = add(info.as_item_info())

    response.headers["location"] = f"/cart/{entity.id}"
    return ItemResponse.from_entity(entity)


@router.get(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested item as one was not found, unfortunate",
        },
    }
)
async def get_one(id: int) -> ItemResponse:
    if item_data[id].deleted:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Item with id {id} not found"
        )
    entity = get_one_item(id)
    if not entity:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /item/{id} was not found, unfortunate",
        )
    return ItemResponse.from_entity(entity)


@router.get("/")
async def get_item_list(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[NonNegativeInt, Query(gt=0)] = 10,
    min_price: float = Query(None, ge=0),
    max_price: float = Query(None, ge=0),
    show_deleted: Optional[bool] = None,
) -> List[ItemResponse]:
    return[ItemResponse.from_entity(e) for e in get_many(
        offset, limit, min_price, max_price, show_deleted,
    )]


@router.put("/{id}")
async def put_item(id: int, info: ItemRequest):
    entity = put_item_by_id(id, info.as_item_info())
    return ItemResponse.from_entity(entity)


@router.patch("/{id}")
async def patch_item(id: int, info: PatchItemRequest) -> ItemResponse:

    entity = patch_item_by_id(id, info)
    return ItemResponse.from_entity(entity)


@router.delete("/{id}")
async def delete_item(id: int) -> ItemResponse:
    entity = delete_item_by_id(id)
    if not entity:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Item with id {id} not found"
        )
    return ItemResponse.from_entity(entity)