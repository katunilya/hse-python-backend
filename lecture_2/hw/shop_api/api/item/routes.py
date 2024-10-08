from fastapi import APIRouter, HTTPException, Response
from http import HTTPStatus
from ...store import queries
from ..item.contracts import ItemRequest, ItemResponse  # Модели для запросов и ответов

router = APIRouter(prefix="/item")

# Создание нового товара
@router.post("/", status_code=HTTPStatus.CREATED, response_model=ItemResponse)
async def create_item(item: ItemRequest, response: Response):
    item_entity = queries.create_item(item.dict())
    response.headers["location"] = f"/item/{item_entity['id']}"
    return item_entity

# Получение товара по его ID
@router.get("/{id}", response_model=ItemResponse)
async def get_item_by_id(id: int):
    item = queries.get_item(id)
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    return item

# Удаление товара
@router.delete("/{id}", status_code=HTTPStatus.OK)
async def delete_item(id: int):
    deleted = queries.delete_item(id)
    if not deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    return {"deleted": True}

# Полное обновление товара (PUT)
@router.put("/{id}", response_model=ItemResponse)
async def update_item(id: int, item_data: ItemRequest):
    item = queries.get_item(id)
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    updated_item = queries.update_item(id, item_data.dict())
    return updated_item

# Частичное обновление товара (PATCH)
@router.patch("/{id}", response_model=ItemResponse)
async def patch_item(id: int, item_data: dict):
    item = queries.get_item(id)
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    # Проверяем, не удалён ли товар
    if item.get("deleted", False):
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, detail="Item is deleted")

    updated_item = queries.patch_item(id, item_data)
    return updated_item