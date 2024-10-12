from http import HTTPStatus
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from lecture_2.hw.shop_api.api.item.contracts import Item, ItemRequest, ItemPatchRequest
from lecture_2.hw.shop_api.store import queries
from starlette.responses import Response

router = APIRouter(prefix="/item")


@router.post(
    "/",
    responses={
        HTTPStatus.CREATED: {
            "description": "Successfully created new item",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Failed to create new item. Something went wrong",
        },
    },
    status_code=HTTPStatus.CREATED,
    response_model=Item,
)
async def create_item(item_request: ItemRequest, response: Response) -> Item:
    try:
        item = queries.create_item(item_request)
        response.headers["location"] = f"/item/{item.id}"
        return item
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))


@router.get(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested item as one was not found",
        },
    },
    status_code=HTTPStatus.OK,
    response_model=Item,
)
async def get_item(id: int) -> Item:
    item = queries.get_item(id)
    if item is None or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    return item


@router.get(
    "/",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned list of items",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return any items for theese params",
        },
    },
    status_code=HTTPStatus.OK,
    response_model=List[Item],
)
async def get_items(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    show_deleted: bool = False,
):
    try:
        items = queries.get_items(offset, limit, min_price, max_price, show_deleted)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))
    if items is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Items not found")
    return items


@router.put(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully changed data of item",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Failed to changed data of item",
        },
    },
    status_code=HTTPStatus.OK,
    response_model=Item,
)
async def update_item(id: int, item_request: ItemRequest) -> Item:
    try:
        updated_item = queries.update_item(id, item_request)
        if updated_item is None:
            raise HTTPException(HTTPStatus.NOT_FOUND, "Item not found")
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))
    return updated_item


@router.patch(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully modified data of item",
        },
        HTTPStatus.NOT_MODIFIED: {
            "description": "Failed to modify data of item",
        },
    },
    status_code=HTTPStatus.OK,
    response_model=Item,
)
async def patch_item(id: int, item_patch_request: ItemPatchRequest) -> Item:
    try:
        patched_item = queries.patch_item(id, item_patch_request)
        if patched_item is None:
            raise HTTPException(HTTPStatus.NOT_FOUND, "Item not found")
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, detail=str(e))
    return patched_item


@router.delete(
    "/{id}",
    responses={
        HTTPStatus.OK: {"description": "Successfully deleted item"},
        HTTPStatus.NOT_FOUND: {"description": "Failed to delete item"},
    },
    status_code=HTTPStatus.OK,
)
async def delete_item(id: int):
    try:
        item = queries.delete_item(id)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    return item
