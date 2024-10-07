from fastapi import APIRouter, HTTPException, Response
from http import HTTPStatus
from ...store import queries

router = APIRouter(prefix="/item")

@router.post("/", status_code=HTTPStatus.CREATED)
async def create_item(item: dict, response: Response):
    item_entity = queries.create_item(item)
    response.headers["location"] = f"/item/{item_entity['id']}"
    return item_entity

@router.get("/{id}", response_model=dict)
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

@router.put("/{id}", response_model=dict)
async def update_item(id: int, item_data: dict):
    item = queries.get_item(id)
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    # Проверяем наличие обязательных полей
    if "name" not in item_data or "price" not in item_data:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Missing fields")

    updated_item = queries.update_item(id, item_data)
    return updated_item


@router.patch("/{id}", response_model=dict)
async def patch_item(id: int, item_data: dict):
    item = queries.get_item(id)
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    # Проверяем, не удалён ли товар
    if item.get("deleted", False):
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, detail="Item is deleted")

    # Обновляем только переданные поля
    updated_item = queries.patch_item(id, item_data)
    return updated_item