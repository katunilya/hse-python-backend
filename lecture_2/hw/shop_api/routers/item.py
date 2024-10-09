import http

from fastapi import APIRouter, Query, HTTPException
from ..repository import items_db, last_item_id
from ..schemas import Item, ItemCreate, ItemPut, ItemUpdate
from typing import Optional, List

router = APIRouter(prefix="/item")


@router.post("/", status_code=http.HTTPStatus.CREATED)
async def create_item(item: ItemCreate) -> Item:
    global last_item_id
    last_item_id += 1
    items_db[last_item_id] = Item(id=last_item_id, name=item.name, price=item.price)
    return items_db[last_item_id]


@router.get("/{item_id}")
async def get_item(item_id: int):
    item = items_db.get(item_id)
    if item is None or item.deleted is True:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Item not found")
    return items_db[item_id]


@router.get("/")
async def get_items(offset: int = Query(0, ge=0),
                    limit: int = Query(10, gt=0),
                    min_price: Optional[float] = Query(None, gt=0),
                    max_price: Optional[float] = Query(None, gt=0),
                    show_deleted: Optional[bool] = False
                    ):
    filtered_items: List[Item] = list(filter(lambda item: (
            (min_price is None or item.price >= min_price) and
            (max_price is None or item.price <= max_price) and
            (show_deleted or not item.deleted)
    ), items_db.values()))
    filtered_items = filtered_items[offset:offset + limit]
    return filtered_items


@router.put("/{item_id}")
async def put_item(item_id: int, item: ItemPut):
    items_db[item_id] = Item(id=item_id, name=item.name, price=item.price, deleted=item.deleted)
    return items_db[item_id]


@router.patch("/{item_id}")
async def patch_item(item_id: int, new_item: Optional[ItemUpdate] = None):
    item = items_db.get(item_id)
    if item and not item.deleted:
        if new_item is None:
            return items_db[item_id]
        new_name = new_item.name if new_item.name is not None else item.name
        new_price = new_item.price if new_item.price is not None else item.price
        items_db[item_id] = Item(id=item_id, name=new_name, price=new_price, deleted=item.deleted)
        return items_db[item_id]
    else:
        raise HTTPException(status_code=http.HTTPStatus.NOT_MODIFIED, detail="Item not modified")


@router.delete("/{item_id}")
async def delete_item(item_id: int):
    item = items_db.get(item_id)
    if not item:
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Item not found")
    items_db[item_id] = Item(id=item_id, name=item.name, price=item.price, deleted=True)
    return items_db[item_id]
