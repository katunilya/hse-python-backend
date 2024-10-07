from fastapi import APIRouter, HTTPException, Response, status, Query, Depends
from lecture_2.hw.shop_api.app.models import NewItem, UpdateItem, Item
from lecture_2.hw.shop_api.app.counter import CounterService
from typing import Dict

router = APIRouter()
items: Dict[int, Item] = {}
item_id_counter = 0

@router.post('/item', status_code=status.HTTP_201_CREATED)
def create_item(
    item: NewItem,
    response: Response,
    counter_service: CounterService = Depends()
):
    new_item_id = counter_service.get_next_item_id()
    new_item = Item(id=new_item_id, name=item.name, price=item.price, deleted=False)
    items[new_item_id] = new_item
    response.headers['location'] = f'/item/{new_item_id}'
    return new_item.model_dump()

@router.get('/item/{id}')
def get_item_by_id(
    id: int
):
    if id not in items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')
    if items[id].deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item deleted')
    return items[id]

@router.get('/item')
def get_item(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    show_deleted: bool = Query(False)
):
    filtered_items = []
    for item in items.values():
        if (
            (min_price is None or item.price >= min_price) and
            (max_price is None or item.price <= max_price) and
            (show_deleted or not item.deleted)
        ):
            filtered_items.append(item)
    return filtered_items[offset:offset + limit]

@router.put('/item/{id}')
def put_item_by_id(
    id: int,
    new_item: NewItem
):
    if id not in items.keys():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item does not exist. Only replacement allowed for existing items')
    item = items[id]
    item.name = new_item.name
    item.price = new_item.price
    return item

@router.patch('/item/{id}')
def patch_item_by_id(
    id: int,
    update_item: UpdateItem
):
    if id not in items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item does not exist. Only replacement allowed for existing items')
    item = items[id]
    if item.deleted:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail='Item deleted')
    if update_item.name is not None:
        item.name = update_item.name
    if update_item.price is not None:
        item.price = update_item.price
    return item

@router.delete('/item/{id}')
def delete_item(
    id: int
):
    if id not in items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found')
    item = items[id]
    item.deleted = True
    return {'message': 'Item deleted'}