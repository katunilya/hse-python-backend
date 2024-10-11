from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional

from pydantic import ValidationError

from ..models.item import Item, ItemUpdate
from ..database import items_db, item_id_counter

router = APIRouter()


@router.post("/item", response_model=Item, status_code=HTTPStatus.CREATED)
def create_item(item: ItemUpdate):
    global item_id_counter
    res = Item(id=item_id_counter, name=item.name, price=item.price)
    item_id_counter += 1
    items_db[res.id] = res
    return res


@router.get("/item/{id}", response_model=Item)
def get_item(id: int):
    item = items_db.get(id)
    if item and not item.deleted:
        return item
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get("/item", response_model=List[Item])
def list_items(
        offset: int = 0,
        limit: int = 10,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        show_deleted: bool = False
):
    if offset < 0:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Offset should be non-negative"
        )
    if limit <= 0:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Limit should be greater than zero"
        )
    if min_price is not None and min_price < 0:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="min_price should be non-negative"
        )
    if max_price is not None and max_price < 0:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="max_price should be non-negative"
        )

    filtered_items = [
        item for item in items_db.values()
        if (show_deleted or not item.deleted)
           and (min_price is None or item.price >= min_price)
           and (max_price is None or item.price <= max_price)
    ]

    return filtered_items[offset:offset + limit]


@router.put("/item/{id}", response_model=Item)
def replace_item(id: int, item: ItemUpdate):
    if id not in items_db or items_db[id].deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.name is not None:
        items_db[id].name = item.name
    if item.price is not None:
        items_db[id].price = item.price
    res = items_db[id]
    return res


DEFAULT_ITEM_UPDATE_FIELDS = {'name', 'price'}


@router.patch("/item/{id}", response_model=Item)
def patch_item(id: int, updated_fields: dict = Body(...)):
    if any(k not in DEFAULT_ITEM_UPDATE_FIELDS for k in updated_fields.keys()):
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Unexpected field")

    if id not in items_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    current_item = items_db[id]
    if current_item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, detail="Cannot change deleted item")

    current_item_data = current_item.model_dump()
    current_item_data.update(updated_fields)

    try:
        patched_item = Item(**current_item_data)
    except ValidationError as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))

    items_db[id] = patched_item
    return patched_item


@router.delete("/item/{id}")
def delete_item(id: int):
    if id in items_db:
        items_db[id].deleted = True
        return {"detail": "Item marked as deleted"}
    else:
        raise HTTPException(status_code=404, detail="Item not found")
