from fastapi import APIRouter, HTTPException, Path, Query, Body, Response
from typing import List, Optional
from http import HTTPStatus

from models import Item, ItemCreate, ItemUpdate, ItemPatch
from database import data_store

router = APIRouter()


@router.post("/", status_code=201, response_model=Item)
def create_item(item_data: ItemCreate, response: Response):
    item_id = data_store.get_new_item_id()
    item = Item(id=item_id, name=item_data.name, price=item_data.price)
    data_store.items_db[item_id] = item
    response.headers["Location"] = f"/item/{item_id}"
    return item.model_dump()


@router.get("/{id}", response_model=Item)
def get_item(id: int = Path(..., ge=1)):
    item = data_store.items_db.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.get("/", response_model=List[Item])
def get_items(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0.0),
    max_price: Optional[float] = Query(None, ge=0.0),
    show_deleted: bool = Query(False),
):
    items = [
        item
        for item in data_store.items_db.values()
        if (show_deleted or not item.deleted)
        and (min_price is None or item.price >= min_price)
        and (max_price is None or item.price <= max_price)
    ]
    return items[offset : offset + limit]


@router.put("/{id}", response_model=Item)
def replace_item(id: int = Path(..., ge=1), item_data: ItemUpdate = Body(...)):
    item = data_store.items_db.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    item.name = item_data.name
    item.price = item_data.price
    return item


@router.patch("/{id}", response_model=Item)
def update_item(id: int = Path(..., ge=1), item_data: ItemPatch = Body(...)):
    item = data_store.items_db.get(id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.deleted:
        return Response(status_code=HTTPStatus.NOT_MODIFIED.value)
    if item_data.name is not None:
        item.name = item_data.name
    if item_data.price is not None:
        item.price = item_data.price
    return item


@router.delete("/{id}")
def delete_item(id: int = Path(..., ge=1)):
    item = data_store.items_db.get(id)
    if not item or item.deleted:
        return {"detail": "Item already deleted"}
    item.deleted = True
    return {"detail": "Item deleted"}
