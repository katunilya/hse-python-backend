from typing import Iterable

from .entities import *
from lecture_2.hw.shop_api.api.storages import (
    cart_data, item_data, cart_id_generator
)

def add(info: CartInfo) -> CartEntity:
    _id = next(cart_id_generator)
    cart_data[_id] = info

    return CartEntity(id=_id, info=info)


def update_cart_price(cart: CartEntity) -> CartEntity:
    priced_cart = cart.model_copy()
    priced_cart.info.price = sum([item.quantity*item_data[item.id].price for item in priced_cart.info.items])
    return priced_cart
 

def get_one_cart(_id: int) -> CartEntity:
    cart = CartEntity(
        id=_id,
        info=cart_data.get(_id, None),
    )
    if not cart:
        return None
    return update_cart_price(cart)


def get_many(
        offset: int = 0,
        limit: int = 10,
        min_price: float | None = None,
        max_price: float | None = None,
        min_quantity: int | None = None,
        max_quantity: int | None = None,
) -> Iterable[CartEntity]:
    _filtered_data = {
        info_id: info for info_id, info in cart_data.items() if
        (min_price is None or info.price >= min_price) and
        (max_price is None or info.price <= max_price) and
        (min_quantity is None or len(info.items) >= min_quantity) and
        (max_quantity is None or len(info.items) <= max_quantity)
    }
    curr = 0
    for id, info in _filtered_data.items():
        if offset <= curr < offset + limit:
            yield CartEntity(id=id, info=info)
        curr += 1


def put_item_in_cart(cart_id: int, item_id: int) -> CartEntity:
    if cart_id not in cart_data or item_id not in item_data:
        return None
    for item in cart_data[cart_id].items:
        if item.id == item_id:
            item.quantity += 1
            return CartEntity(id=cart_id, info=cart_data[cart_id])
    item_to_put = ItemInCart(
        id=item_id,
        name=item_data[item_id].name,
        quantity=1,
        available=not item_data[item_id].deleted,
    )
    cart_data[cart_id].items.append(item_to_put)
    return CartEntity(id=cart_id, info=cart_data[cart_id])