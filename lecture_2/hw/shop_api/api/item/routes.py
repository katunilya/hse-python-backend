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