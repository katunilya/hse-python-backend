from typing import Iterable

from lecture_2.hw.shop_api.store.item_store.models import ItemInfo, PatchItemInfo

from .models import CartEntity, CartInfo, ItemsInCartInfo
from .. import item_store

_data = dict[int, CartEntity]()


def int_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1


_id_generator = int_id_generator()


def add() -> int:
    _id = next(_id_generator)
    _data[_id] = CartEntity(id_=_id, info=CartInfo(id_=_id, items={}, price=0.0))
    return _id


def get_one(id_: int) -> CartEntity | None:
    print(id_)
    if id_ in _data:
        return _data[id_]

    return None


def get_many(
    offset: int = 0,
    limit: int = 10,
    min_price: float | None = None,
    max_price: float | None = None,
    min_quantity: int | None = None,
    max_quantity: int | None = None,
) -> Iterable[CartEntity]:
    filtered_carts = _data.values()
    if min_price is not None:
        filtered_carts = (
            cart for cart in filtered_carts if cart.info.price >= min_price
        )
    if max_price is not None:
        filtered_carts = (
            cart for cart in filtered_carts if cart.info.price <= max_price
        )
    if min_quantity is not None:
        filtered_carts = (
            cart
            for cart in filtered_carts
            if sum(item.quantity for _, item in cart.info.items.items()) >= min_quantity
        )
    if max_quantity is not None:
        filtered_carts = (
            cart
            for cart in filtered_carts
            if sum(item.quantity for _, item in cart.info.items.items()) <= max_quantity
        )

    curr = 0
    for cart in filtered_carts:
        if offset <= curr < offset + limit:
            yield cart

        curr += 1


def add_item(cart_id: int, item_id: int) -> ItemsInCartInfo | None:
    if cart_id not in _data:
        return None

    item = item_store.get_one(item_id)
    if item is None:
        return None

    if item_id in _data[cart_id].info.items:
        _data[cart_id].info.items[item_id].quantity += 1
    else:
        _data[cart_id].info.items[item_id] = ItemsInCartInfo(
            id_=item_id, quantity=1, name=item.info.name, available=not item.deleted
        )

    _data[cart_id].info.price += item.info.price
    return _data[cart_id].info


def update_item_info(
    item_id: int, item_info: ItemInfo, patch_info: PatchItemInfo
) -> None:
    for cart in _data.values():
        if item_id in cart.info.items:
            if patch_info.name is not None:
                cart.info.items[item_id].name = patch_info.name
            if patch_info.price is not None:
                cart.info.price -= item_info.price * cart.info.items[item_id].quantity
                cart.info.price += patch_info.price * cart.info.items[item_id].quantity
    return
