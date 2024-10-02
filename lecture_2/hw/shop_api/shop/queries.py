from typing import Iterable, Tuple

from lecture_2.hw.shop_api.shop.models import (
    Cart,
    CartItem,
    Item,
    ItemInfo,
    PatchItemInfo,
)
from ..cart.cart_grpc import _carts

_items = dict[int, ItemInfo]()


def int_id_gen() -> Iterable[int]:
    i = 0

    while True:
        yield i
        i += 1


_id_gen = int_id_gen()


def get_cart(id: int) -> Cart | None:
    return _carts.get(id, None)


def get_carts(
    limit: int, offset: int, min_price: float = 0, max_price: float = float("inf")
) -> Iterable[Cart]:
    curr = 0

    for _, cart in _carts.items():
        if (
            offset <= curr < offset + limit
            and cart.price >= min_price
            and cart.price <= max_price
        ):
            yield cart

        curr += 1


def get_items(
    limit: int, offset: int, min_price: float = 0, max_price: float = float("inf")
) -> Iterable[Item]:
    curr = 0

    for _, item in _items.items():
        if (
            offset <= curr < offset + limit
            and item.price >= min_price
            and item.price <= max_price
        ):
            yield item

        curr += 1


def add_item_to_cart(cart_id: int, item_id: int) -> Tuple[Cart, ItemInfo]:
    cart = _carts.get(cart_id, None)
    item_info = _items.get(item_id, None)

    if cart is None or item_info is None:
        return cart, item_info

    item = Item(id=item_id, info=item_info)

    for cart_item in cart.items:
        id_ = cart_item.item.id

        if item.id == id_:
            cart_item.quantity += 1
            cart.price += item.info.price

            return cart, item_info

    cart.items.append(CartItem(item, quantity=1))

    return cart, item_info


def get_item(id: int) -> Item:
    info = _items.get(id, None)

    if info is None:
        return info

    return Item(id=id, info=info)


def add_item(info: ItemInfo) -> Item:
    _id = next(_id_gen)
    _items[_id] = info

    return Item(id=_id, info=info)


def update_item(id: int, info: ItemInfo) -> Item:
    if id not in _items:
        return None

    _items[id] = info

    return Item(id=id, info=info)


def patch_item(id: int, info: PatchItemInfo) -> Item:
    if id not in _items:
        return None

    item_info = _items.get(id)
    item_info.name = info.name
    item_info.price = info.price

    _items[id] = item_info

    return Item(id=id, info=item_info)


def delete_item(id: int) -> Item:
    if id not in _items:
        return None

    item_info = _items.get(id)
    item_info.deleted = True

    _items[id] = item_info

    return Item(id=id, info=item_info)
