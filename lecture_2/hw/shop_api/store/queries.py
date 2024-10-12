from typing import List, Optional

from lecture_2.hw.shop_api.store.models import Cart, CartItem, Item
from lecture_2.hw.shop_api.api.item.contracts import ItemRequest, ItemPatchRequest

_cart_data = dict[int, Cart]()
_item_data = dict[int, Item]()
_cart_id_counter = 0
_item_id_counter = 0


def create_cart() -> int:
    global _cart_id_counter
    _cart_id_counter += 1
    cart = Cart(id=_cart_id_counter)
    _cart_data[_cart_id_counter] = cart
    return cart


def get_cart(cart_id: int) -> Optional[Cart]:
    return _cart_data.get(cart_id)


def get_carts(
    offset: int,
    limit: int,
    min_price: Optional[float],
    max_price: Optional[float],
    min_quantity: Optional[int],
    max_quantity: Optional[int],
) -> List[Cart]:
    carts = list(_cart_data.values())

    if not carts:
        return None

    carts = [
        cart
        for cart in carts
        if ((min_price is None) or (cart.price >= min_price))
        & ((max_price is None) or (cart.price <= max_price))
    ]

    if min_quantity is not None:
        carts = [
            cart
            for cart in carts
            if sum(item.quantity for item in cart.items) >= min_quantity
        ]

    if max_quantity is not None:
        carts = [
            cart
            for cart in carts
            if sum(item.quantity for item in cart.items) <= max_quantity
        ]

    return carts[offset : offset + limit]


def add_item_to_cart(cart_id: int, item_id: int) -> Cart:
    cart = get_cart(cart_id)
    item = get_item(item_id)
    if cart is None:
        raise ValueError(f"Cart with id {cart_id} not found.")
    if item is None:
        raise ValueError(f"Item with id {item_id} not found.")

    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            break
    else:
        cart.items.append(
            CartItem(id=item.id, name=item.name, quantity=1, available=True)
        )

    cart.price += item.price

    return cart


def create_item(item_request: ItemRequest) -> Item:
    global _item_id_counter
    _item_id_counter += 1
    item = Item(id=_item_id_counter, name=item_request.name, price=item_request.price)
    _item_data[_item_id_counter] = item
    return item


def get_item(item_id: int) -> Optional[Item]:
    return _item_data.get(item_id)


def get_items(
    offset: int,
    limit: int,
    min_price: Optional[float],
    max_price: Optional[float],
    show_deleted: bool,
) -> List[Item]:
    items = list(_item_data.values())
    if not items:
        return None

    items = [
        item
        for item in items
        if ((min_price is None) or (item.price >= min_price))
        & ((max_price is None) or (item.price <= max_price))
        & (show_deleted or (not item.deleted))
    ]
    return items[offset : offset + limit]


def update_item(item_id: int, item_request: ItemRequest) -> Item:
    item = get_item(item_id)

    if item is None or item.deleted:
        return None
    item.name = item_request.name
    item.price = item_request.price
    return item


def patch_item(item_id: int, item_patch_request: ItemPatchRequest) -> Item:
    item = get_item(item_id)
    if item is None or item.deleted:
        return None

    if item_patch_request.name is not None:
        item.name = item_patch_request.name
    if item_patch_request.price is not None:
        item.price = item_patch_request.price

    return item


def delete_item(item_id: int) -> Optional[Item]:
    item = _item_data.get(item_id)
    if item is None:
        return None

    item.deleted = True
    return item
