from fastapi import APIRouter, HTTPException, Response, Query
from http import HTTPStatus
from typing import List, Optional
from lecture_2.hw.shop_api.store import queries
from lecture_2.hw.shop_api.api.item.contracts import ItemResponse, ItemRequest

router = APIRouter(prefix="/item")

@router.post("/", status_code=HTTPStatus.CREATED, response_model=ItemResponse)
async def create_item(item: ItemRequest, response: Response):
    item_entity = queries.create_item(item)
    response.headers["location"] = f"/item/{item_entity.id}"
    return item_entity

@router.get("/{id}", response_model=ItemResponse)
async def get_item_by_id(id: int):
    item = queries.get_item(id)
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    return item

@router.delete("/{id}", status_code=HTTPStatus.OK)
async def delete_item(id: int):
    deleted = queries.delete_item(id)
    if not deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    return {"deleted": True}

@router.put("/{id}", response_model=ItemResponse)
async def update_item(id: int, item_data: ItemRequest):
    updated_item = queries.update_item(id, item_data)
    if not updated_item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found or deleted")
    return updated_item

@router.patch("/{id}", response_model=ItemResponse)
async def patch_item(id: int, item_data: ItemRequest):
    updated_item = queries.patch_item(id, item_data)
    if not updated_item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found or deleted")
    return updated_item

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