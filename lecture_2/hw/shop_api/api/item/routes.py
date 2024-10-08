from fastapi import APIRouter, HTTPException, Response, Query
from http import HTTPStatus
from typing import List, Optional
from lecture_2.hw.shop_api.store import queries
from lecture_2.hw.shop_api.api.item.contracts import ItemResponse, ItemRequest, ItemPatchRequest


router = APIRouter(prefix="/item")


@router.post("/", status_code=HTTPStatus.CREATED, response_model=ItemResponse)
async def create_item(item: ItemRequest, response: Response):
    item_entity = queries.create_item(item)
    response.headers["location"] = f"/item/{item_entity.id}"
    return item_entity


@router.get("/{id}", response_model=ItemResponse)
async def get_item_by_id(id: int):
    item = queries.get_item(id)
    if not item or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found or deleted")
    return item


@router.put("/{id}", response_model=ItemResponse)
async def update_item(id: int, item_data: ItemRequest):
    updated_item = queries.update_item(id, item_data)
    if not updated_item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found or deleted")
    return updated_item


@router.patch(
    "/{id}",
    responses={
        HTTPStatus.OK: {"description": "Successfully modified data of item"},
        HTTPStatus.NOT_FOUND: {"description": "Item not found"},
        HTTPStatus.NOT_MODIFIED: {"description": "Item is deleted or cannot be modified"},
    },
    status_code=HTTPStatus.OK,
    response_model=ItemResponse,
)
async def patch_item(id: int, item_patch_request: ItemPatchRequest) -> ItemResponse:
    try:
        patched_item = queries.patch_item(id, item_patch_request)
        if patched_item is None:
            raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, detail="Item not found or deleted")
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


@router.get("/", response_model=List[ItemResponse])
async def get_item_list(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    show_deleted: bool = Query(False)
):
    items = queries.get_items(offset, limit, min_price, max_price, show_deleted)
    return items