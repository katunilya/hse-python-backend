from typing import Iterable, Tuple

from .models import (
    Cart,
    CartItem,
    Item,
    ItemInfo,
    PatchItemInfo,
)

# from ..cart.cart_grpc import _carts

_items = dict[int, ItemInfo]()
_carts = dict[int, Cart]()


def int_id_gen() -> Iterable[int]:
    i = 0

    while True:
        yield i
        i += 1


_id_gen = int_id_gen()


def post_cart() -> Cart:
    _id = next(_id_gen)
    _carts[_id] = Cart(id=_id, items=[])

    return _id, _carts[_id]


def get_cart(id: int) -> Cart | None:
    return _carts.get(id, None)


def get_carts(
    limit: int,
    offset: int,
    min_price: float,
    max_price: float,
    min_quantity: int,
    max_quantity: int,
) -> Iterable[Cart]:
    curr = 0

    if max_price is None:
        max_price = float("inf")

    if max_quantity is None:
        max_quantity = float("inf")

    for _, cart in _carts.items():
        if (
            offset <= curr < offset + limit
            and cart.price >= min_price
            and cart.price <= max_price
            and sum(item.quantity for item in cart.items) >= min_quantity
            and sum(item.quantity for item in cart.items) <= max_quantity
        ):
            yield cart

        curr += 1


def get_items(
    limit: int, offset: int, min_price: float, max_price: float
) -> Iterable[Item]:
    curr = 0

    if max_price is None:
        max_price = float("inf")

    for id, item in _items.items():
        if (
            offset <= curr < offset + limit
            and item.price >= min_price
            and item.price <= max_price
            and not item.deleted
        ):
            yield Item(id, item)

        curr += 1


def add_item_to_cart(cart_id: int, item_id: int) -> Tuple[Cart, ItemInfo]:
    cart = _carts.get(cart_id, None)
    item_info = _items.get(item_id, None)

    if cart is None or item_info is None or item_info.deleted:
        return cart, item_info

    item = Item(id=item_id, info=item_info)

    for cart_item in cart.items:
        id_ = cart_item.item.id

        if item_id == id_:
            cart_item.quantity += 1
            cart.price += item.info.price

            return cart, item_info

    cart.items.append(CartItem(item, quantity=1))
    cart.price += item.info.price

    return cart, item_info


def get_item(id: int) -> Item:
    info = _items.get(id, None)

    if info is None:
        return None

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

    if info.name is not None:
        item_info.name = info.name

    if info.price is not None:
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
