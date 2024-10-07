from fastapi import APIRouter, HTTPException, Response, status
from lecture_2.hw.shop_api.app.models import Cart, CartItem
from lecture_2.hw.shop_api.app.items import items
from lecture_2.hw.shop_api.app.counter import CounterService
from fastapi import Depends, Query
from typing import Dict

router = APIRouter()
carts: Dict[int, Cart] = {}
cart_id_counter = 0

@router.post('/cart', status_code=status.HTTP_201_CREATED)
def create_cart(
    response: Response,
    counter_service: CounterService = Depends()
):
    new_cart_id = counter_service.get_next_cart_id()
    carts[new_cart_id] = Cart(id=new_cart_id)
    response.headers['location'] = f'/cart/{new_cart_id}'
    return {'id': new_cart_id}

@router.post('/cart/{cart_id}/add/{item_id}', status_code=status.HTTP_200_OK)
def add_item_to_cart(
    cart_id: int,
    item_id: int
):
    if cart_id not in carts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Cart not found')
    if item_id not in items or items[item_id].deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Item not found or deleted')
    
    item = items[item_id]
    cart = carts[cart_id]

    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            break
    else:
        cart.items.append(CartItem(id=item.id, name=item.name, quantity=1, available=True))

    cart.price = sum(cart_item.quantity * items[cart_item.id].price for cart_item in cart.items)
    return cart

@router.get('/cart/{cart_id}')
def get_cart_by_id(
    cart_id: int
):
    if cart_id not in carts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Cart not found')
    return carts[cart_id]

@router.get('/cart')
def get_carts(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    min_quantity: int | None = Query(None, ge=0),
    max_quantity: int | None = Query(None, ge=0)
):
    filtered_carts = []
    for cart in carts.values():
        if (
            (min_price is None or cart.price >= min_price) and
            (max_price is None or cart.price <= max_price) and
            (min_quantity is None or sum(item.quantity for item in cart.items) >= min_quantity) and
            (max_quantity is None or sum(item.quantity for item in cart.items) <= max_quantity)
        ):
            filtered_carts.append(cart)
    return filtered_carts[offset:offset + limit]