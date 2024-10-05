from typing import Iterable

from lecture_2.hw.shop_api.models import Item, ItemInfo, PatchItemInfo, ItemInCart, Cart


def int_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1


_item_id_generator = int_id_generator()
items = dict[int, ItemInfo]()


def add_item(item_info: ItemInfo) -> Item:
    _id = next(_item_id_generator)
    items[_id] = item_info

    return Item(id=_id, info=item_info)


def get_item_by_id(item_id: int) -> Item | None:
    if item_id not in items or items[item_id].deleted:
        return None

    return Item(id=item_id, info=items[item_id])


def get_many_items(
    offset: int = 0,
    limit: int = 10,
    min_price: float | None = None,
    max_price: float | None = None,
    show_deleted: bool = False,
) -> Iterable[Item]:
    if min_price is None:
        min_price = float('-inf')
    if max_price is None:
        max_price = float('inf')
    cur = 0
    for item_id, item_info in items.items():
        if offset <= cur < offset + limit and min_price <= item_info.price <= max_price:
            if not show_deleted:
                if not item_info.deleted:
                    yield Item(item_id, item_info)
                    cur += 1
            else:
                yield Item(item_id, item_info)
                cur += 1
        # cur += 1


def put_item(item_id, item_info: ItemInfo) -> Item | None:
    if item_id not in items:
        return None

    if item_info.price is not None:
        items[item_id].price = item_info.price
    if item_info.name is not None:
        items[item_id].name = item_info.name
    if item_info.deleted is not None:
        items[item_id].deleted = item_info.deleted

    return Item(id=item_id, info=items[item_id])


def patch_item(item_id: int, item_info: PatchItemInfo) -> Item | str | None:
    if item_id not in items:
        return 'not found'
    else:
        if items[item_id].deleted:
            return 'deleted'
        if item_info.price is not None:
            items[item_id].price = item_info.price
        if item_info.name is not None:
            items[item_id].name = item_info.name

        return Item(id=item_id, info=items[item_id])


def delete_item(item_id: int) -> str | None:
    if item_id in items:
        if items[item_id].deleted:
            return 'already deleted'
        else:
            items[item_id].deleted = True
            return 'deleted'
    else:
        return 'not found'

