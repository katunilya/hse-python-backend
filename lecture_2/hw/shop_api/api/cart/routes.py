from fastapi import APIRouter, HTTPException, Response
from http import HTTPStatus
from ...store import queries

router = APIRouter(prefix="/cart")

@router.post("/", status_code=HTTPStatus.CREATED)
async def create_cart(response: Response):
    cart = queries.create_cart()
    response.headers["location"] = f"/cart/{cart['id']}"
    return cart

@router.get("/{id}", response_model=dict)
async def get_cart_by_id(id: int):
    cart = queries.get_cart(id)
    if not cart:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")
    return cart

@router.post("/{cart_id}/add/{item_id}")
async def add_item_to_cart(cart_id: int, item_id: int):
    result = queries.add_item(cart_id, item_id)
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item or Cart not found")
    return result