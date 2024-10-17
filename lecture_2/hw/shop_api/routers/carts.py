from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Response
from typing import List, Optional

from ..models.cart import Cart, CartItem
from ..database import carts_db, cart_id_counter, items_db

router = APIRouter()


@router.post("/cart", status_code=HTTPStatus.CREATED)
def create_cart(response: Response):
    cart_id = len(carts_db) + 1
    cart = Cart(id=cart_id)
    carts_db[cart_id] = cart
    response.headers["Location"] = f"/cart/{cart_id}"
    return cart


@router.get("/cart/{id}", response_model=Cart)
def get_cart(id: int):
    cart = carts_db.get(id)
    if cart:
        return cart
    else:
        raise HTTPException(status_code=404, detail="Cart not found")


@router.get("/cart", response_model=List[Cart])
def list_cart(
        offset: int = 0,
        limit: int = 10,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_quantity: Optional[int] = None,
        max_quantity: Optional[int] = None
):
    if offset < 0:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Offset should be non-negative"
        )
    if limit <= 0:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Limit should be greater than 0"
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
    if min_quantity is not None and min_quantity < 0:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="min_quantity should be non-negative"
        )
    if max_quantity is not None and max_quantity < 0:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="max_quantity should be non-negative"
        )
    carts_list = list(carts_db.values())[offset:]

    filtered_carts = []

    for cart in carts_list:
        if len(filtered_carts) >= limit:
            break

        total_price = cart.price
        total_quantity = sum(item.quantity for item in cart.items)

        if (
                (min_price is None or total_price >= min_price) and
                (max_price is None or total_price <= max_price) and
                (min_quantity is None or total_quantity >= min_quantity) and
                (max_quantity is None or total_quantity <= max_quantity)
        ):
            filtered_carts.append(cart)

    return filtered_carts


@router.post("/cart/{cart_id}/add/{item_id}")
def add_item_to_cart(cart_id: int, item_id: int):
    cart = carts_db.get(cart_id)
    item = items_db.get(item_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found or deleted")

    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            break
    else:
        cart_item = CartItem(
            id=item.id,
            name=item.name,
            quantity=1,
            available=not item.deleted
        )
        cart.items.append(cart_item)
    cart.price += item.price
    return {"detail": "Item added to cart"}
