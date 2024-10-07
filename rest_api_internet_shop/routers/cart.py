from fastapi import APIRouter, HTTPException, Path, Query, Response
from typing import List, Optional

from rest_api_internet_shop.models import Cart, CartResponse, CartItem
from rest_api_internet_shop.database import data_store

router = APIRouter()

@router.post("/", status_code=201)
def create_cart(response: Response):
    cart_id = data_store.get_new_cart_id()
    cart = Cart(id=cart_id)
    data_store.carts_db[cart_id] = cart
    response.headers["Location"] = f"/cart/{cart_id}"
    return {"id": cart_id}

@router.get("/", response_model=List[CartResponse])
def get_carts(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0.0),
    max_price: Optional[float] = Query(None, ge=0.0),
    min_quantity: Optional[int] = Query(None, ge=0),
    max_quantity: Optional[int] = Query(None, ge=0),
):
    carts = []
    for cart in data_store.carts_db.values():
        cart_response = CartResponse(**cart.model_dump())
        cart_response.update_item_availability(data_store.items_db)
        cart_response.calculate_totals(data_store.items_db)

        if all([
            min_price is None or cart_response.price >= min_price,
            max_price is None or cart_response.price <= max_price,
            min_quantity is None or cart_response.quantity >= min_quantity,
            max_quantity is None or cart_response.quantity <= max_quantity,
        ]):
            carts.append(cart_response)
    return carts[offset : offset + limit]

@router.get("/{id}", response_model=CartResponse)
def get_cart(id: int = Path(..., ge=1)):
    cart = data_store.carts_db.get(id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    cart_response = CartResponse(**cart.model_dump())
    cart_response.update_item_availability(data_store.items_db)
    cart_response.calculate_totals(data_store.items_db)
    return cart_response

@router.post("/{cart_id}/add/{item_id}")
def add_item_to_cart(
    cart_id: int = Path(..., ge=1),
    item_id: int = Path(..., ge=1)
):
    cart = data_store.carts_db.get(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    item = data_store.items_db.get(item_id)
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found or deleted")

    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            break
    else:
        cart.items.append(CartItem(id=item_id))

    return {"detail": "Item added to cart"}
