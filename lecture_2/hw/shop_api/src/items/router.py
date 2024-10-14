from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, HTTPException, Response, Query

from lecture_2.hw.shop_api.src.items.schema import Item, ItemDto
from lecture_2.hw.shop_api.utils import generate_id
from lecture_2.hw.shop_api.storage import items
from pydantic import NonNegativeInt, PositiveInt, PositiveFloat

item_router = APIRouter()

@item_router.post("/", status_code=HTTPStatus.CREATED)
def add_item(item_dto: ItemDto, response: Response):
    id = generate_id()
    item = Item(id=id, name=item_dto.name, price=item_dto.price, deleted = False)
    items[id] = item
    response.headers["location"] = f"/item/{item.id}"
    return item


@item_router.get("/{id}")
def get_item(id: int):
    item = items.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    return item


@item_router.get("/")
def get_items(
    offset: Annotated[NonNegativeInt, Query()] = 0, 
    limit: Annotated[PositiveInt, Query()] = 10, 
    min_price: Annotated[PositiveFloat, Query()] = None, 
    max_price: Annotated[PositiveFloat, Query()] = None, 
    show_deleted: bool = False
):
    result = [
        item for item in items.values()
        if (show_deleted or not item.deleted)
        and (min_price is None or item.price >= min_price)
        and (max_price is None or item.price <= max_price)
    ]
    return result[offset:offset+limit]


@item_router.put("/{id}")
def update_item(id: int, updated_item: ItemDto):
    item = items.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    items[id] = Item(id=id, name=updated_item.name, price=updated_item.price)
    return items[id]


@item_router.patch("/{id}")
def partial_update_item(id: int, updated_data: dict):
    item = items.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, detail="Item not found")
    
    for key, value in updated_data.items():
        if not key in item.__dict__.keys() or key == "deleted" or key == "id":
            raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, "Unavailable key")
    
    for key, value in updated_data.items():
        setattr(item, key, value)

    return item


@item_router.delete("/{id}")
def delete_item(id: int):
    item = items.get(id)
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    item.deleted = True