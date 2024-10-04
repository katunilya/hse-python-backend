from typing import Iterable

from lecture_2.hw.shop_api.store.models import (
    CartEntity,
    CartInfo,
    ItemEntity,
    CartItemEntity,
    ItemInfo,
    PatchItemInfo,
)


_data_item = dict[int, ItemInfo]()
_data_cart = dict[int, CartInfo]()


def int_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1


_item_id_generator = int_id_generator()
_cart_id_generator = int_id_generator()


def add_item(info: ItemInfo) -> ItemEntity:
    _id = next(_item_id_generator)
    _data_item[_id] = info

    return ItemEntity(_id, info)


def add_cart() -> CartEntity:
    _id = next(_cart_id_generator)
    _data_cart[_id] = CartInfo()
    return CartEntity(_id, price=0.0, items=[])


def get_item(item_id: int) -> ItemEntity | None:
    if item_id not in _data_item or _data_item[item_id].deleted:
        return None
    return ItemEntity(item_id, _data_item[item_id])


def delete_item(item_id: int) -> None:
    if item_id in _data_item:
        _data_item[item_id].deleted = True


def add_item_to_cart(cart_id: int, item_id: int):
    if cart_id not in _data_cart:
        return None
    _data_cart[cart_id].items[item_id] += 1


def update_item(item_id: int, info: ItemInfo) -> ItemEntity | None:
    if item_id not in _data_item:
        return None
    _data_item[item_id] = info
    return ItemEntity(id=item_id, info=info)


def get_many_items(
    offset: int = 0,
    limit: int = 10,
    min_price: float | None = None,
    max_price: float | None = None,
    show_deleted: bool = False,
) -> Iterable[ItemEntity]:
    curr = 0
    for id, info in _data_item.items():
        if offset <= curr < offset + limit and check_predicate_item(
            info, min_price, max_price, show_deleted
        ):
            yield ItemEntity(id, info)

        curr += 1


def get_many_carts(
    offset: int = 0,
    limit: int = 10,
    min_price: float | None = None,
    max_price: float | None = None,
    min_quantity: int | None = None,
    max_quantity: int | None = None,
) -> Iterable[CartEntity]:
    curr = 0
    for cart_id in _data_item:
        cartentity = CartEntity(
            cart_id, price=get_cart_price(cart_id), items=get_cart_items(cart_id)
        )
        if offset <= curr < offset + limit and check_predicate_cart(
            cartentity, min_price, max_price, min_quantity, max_quantity
        ):
            yield cartentity
        curr += 1


def check_predicate_cart(
    entity: CartEntity,
    min_price: float | None = None,
    max_price: float | None = None,
    min_quantity: int | None = None,
    max_quantity: int | None = None,
):
    if min_price is not None and entity.price < min_price:
        return False
    if max_price is not None and entity.price > max_price:
        return False
    quantity = 0
    for q in entity.items:
        quantity += q.quantity
    if min_quantity is not None and quantity < min_quantity:
        return False
    if max_quantity is not None and quantity > max_quantity:
        return False
    return True


def check_predicate_item(
    info: ItemInfo,
    min_price: float | None = None,
    max_price: float | None = None,
    show_deleted: bool = False,
):
    if min_price is not None and info.price < min_price:
        return False
    if max_price is not None and info.price > max_price:
        return False
    if info.deleted and not show_deleted:
        return False
    return True


def patch_item(id: int, patch_info: PatchItemInfo) -> ItemEntity | None:
    if id not in _data_item:
        return None

    if _data_item[id].deleted:
        return None

    if patch_info.name is not None:
        _data_item[id].name = patch_info.name

    if patch_info.price is not None:
        _data_item[id].price = patch_info.price

    return ItemEntity(id=id, info=_data_item[id])


def get_cart(cart_id: int) -> CartEntity | None:
    if cart_id not in _data_cart:
        return None
    return CartEntity(
        cart_id, price=get_cart_price(cart_id), items=get_cart_items(cart_id)
    )


def get_cart_price(cart_id: int) -> float:
    sum = 0.0
    for item_id, quantity in _data_cart[cart_id].items.items():
        sum += _data_item[item_id].price * quantity
    return sum


def get_cart_items(cart_id: int) -> list[CartItemEntity]:
    return [
        CartItemEntity(
            item_id, _data_item[item_id].name, quantity, not _data_item[item_id].deleted
        )
        for item_id, quantity in _data_cart[cart_id].items.items()
    ]
