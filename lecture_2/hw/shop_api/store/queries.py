from typing import Iterable

from fastapi import HTTPException
from starlette import status

from .models import CartEntity, ItemEntity, ItemInCart

_carts = dict[int, CartEntity]()
_items = dict[int, ItemEntity]()

def int_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1


_cart_id_gen = int_id_generator()
_item_id_gen = int_id_generator()


def create_cart() -> CartEntity:
    _id = next(_cart_id_gen)
    _carts[_id] = CartEntity(_id)
    return _carts[_id]


def get_cart_by_id(id: int):
    return _carts.get(id)


def create_item(name="", price=0, deleted=False) -> ItemEntity:
    _id = next(_item_id_gen)
    _items[_id] = ItemEntity(id=_id, name=name, price=price, deleted=deleted)
    return _items[_id]


def get_many_carts(offset: int, limit: int, min_price: float = 0, max_price: float = float('inf'),
                   min_quantity: int = 0,
                   max_quantity: int = float('inf')) -> Iterable[CartEntity]:
    curr = 0
    for cart in _carts.values():
        if (offset <= curr < offset + limit and
                min_price <= cart.price <= max_price and
                min_quantity <= cart.quantity <= max_quantity):
            yield cart
        curr += 1



def get_item_by_id(id: int):
    item = _items.get(id)
    if item and not item.deleted:
        return _items.get(id)


def get_many_items(offset: int, limit: int, min_price: float = 0, max_price: float = float('inf'),
                   show_deleted: bool = False) -> Iterable[ItemEntity]:
    curr = 0
    for item in _items.values():
        if (offset <= curr < offset + limit and
                min_price <= item.price <= max_price and
                (show_deleted or not item.deleted)):
            yield item
        curr += 1

def add_item_to_cart(cart_id: int, item_id: int):
    if cart_id not in _carts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Корзины с id = {cart_id} не существует")
    if item_id not in _items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Товара с id = {item_id} не существует")

    cart = _carts[cart_id]
    items = [item for item in cart.items if item.id == item_id]

    if len(items) > 0:
        item = items[0]
        cart.quantity += 1
        cart.price += _items[item_id].price
        item.quantity += 1
    else:
        item = _items[item_id]
        cart.quantity += 1
        cart.price += item.price
        cart.items.append(ItemInCart(id=item_id, name=item.name, quantity=1, available=not item.deleted))

def update_item(id, name, price):
    if name is None or price is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Недостаточно аргументов")
    item_old = _items.get(id)
    if item_old is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Товара с id = {id} не существует")

    price_diff = price - _items[id].price
    item_old.name = name
    item_old.price = price
    item_old.deleted = False

    for cart in _carts.values():
        for item in cart.items:
            if item.id == id:
                item.name = name
                if item.available:
                    cart.price += price_diff
                item.available = True
    return _items[id]

def patch_item(id, name, price):
    item_old = _items.get(id)
    print("AAA", item_old)
    if item_old.deleted:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f"Товар с id = {id} удалён")

    if name is None:
        name = _items[id].name
    if price is None:
        price = _items[id].price
    update_item(id, name, price)
    return _items[id]

def delete_item(id):
    _items[id].deleted = True

    for cart in _carts.values():
        for item in cart.items:
            if item.id == id:
                cart.price -= item.price
                cart.quantity -= item.quantity
    return _items[id]