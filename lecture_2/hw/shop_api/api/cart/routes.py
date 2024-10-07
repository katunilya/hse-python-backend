from fastapi import APIRouter, HTTPException, Response
from http import HTTPStatus
from ...store import queries

router = APIRouter(prefix="/cart")

@router.post("/", status_code=HTTPStatus.CREATED)
async def create_cart(response: Response):
    cart = queries.create_cart()
    response.headers["location"] = f"/cart/{cart['id']}"
    return cart

@router.get("/", response_model=list)
async def get_cart_list(min_price: float = None, max_price: float = None, offset: int = 0, limit: int = 10):
    if offset < 0 or limit <= 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid pagination parameters")

    filtered_carts = list(_data_carts.values())

    if min_price is not None:
        filtered_carts = [cart for cart in filtered_carts if cart["price"] >= min_price]
    if max_price is not None:
        filtered_carts = [cart for cart in filtered_carts if cart["price"] <= max_price]

    return filtered_carts[offset:offset + limit]

@router.post("/{cart_id}/add/{item_id}")
async def add_item_to_cart(cart_id: int, item_id: int):
    result = queries.add_item(cart_id, item_id)
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item or Cart not found")
    return result