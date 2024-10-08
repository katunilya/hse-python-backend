from fastapi import APIRouter, Query
from repository import items_db, last_item_id
from schemas import Item, ItemCreate, ItemPut, ItemUpdate
from typing import Optional, List

router = APIRouter(prefix="/item")


@router.post("/")
async def create_item(item: ItemCreate) -> Item:
    global last_item_id
    last_item_id += 1
    items_db[last_item_id] = Item(id=last_item_id, name=item.name, price=item.price)
    return items_db[last_item_id]


@router.get("/{item_id}")
async def get_item(item_id: int):
    return items_db[item_id]


@router.get("/")
async def get_items(offset: int = Query(0, ge=0),
                   limit: int = Query(10, gt=0),
                   min_price: Optional[float] = None,
                   max_price: Optional[float] = None,
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
async def patch_item(item_id: int, item: ItemUpdate):
    items_db[item_id] = Item(id=item_id, name=item.name, price=item.price, deleted=items_db[item_id].deleted)
    return items_db[item_id]


@router.delete("/{item_id}")
async def delete_item(item_id: int):
    items_db[item_id] = Item(id=item_id, name=items_db[item_id].name, price=items_db[item_id].price, deleted=True)
    return items_db[item_id]


