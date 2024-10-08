from typing import Iterable

from .models import ItemEntity, ItemInfo, PatchItemInfo
from .. import cart_store
_data = dict[int, ItemEntity]()


def int_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1


_id_generator = int_id_generator()


def add(info: ItemInfo) -> ItemEntity:
    _id = next(_id_generator)
    _data[_id] = ItemEntity(id_=_id, info=info, deleted=False)
    return _data[_id]


def delete(id_: int) -> None:
    if id_ in _data:
        _data[id_].deleted = True


def get_one(id_: int) -> ItemEntity | None:
    if id_ in _data:
        if not _data[id_].deleted:
            return _data[id_]

    return None


def get_many(
    offset: int = 0,
    limit: int = 10,
    min_price: float | None = None,
    max_price: float | None = None,
    show_deleted: bool = False,
) -> Iterable[ItemEntity]:
    filtered_items = _data.values()
    if min_price is not None:
        filtered_items = (
            item for item in filtered_items if item.info.price >= min_price
        )
    if max_price is not None:
        filtered_items = (item for item in filtered_items if item.info.price <= max_price)
    if not show_deleted:
        filtered_items = (item for item in filtered_items if not item.deleted)

    curr = 0
    for item in filtered_items:
        if offset <= curr < offset + limit:
            yield item

        curr += 1


def update(id_: int, info: ItemInfo) -> ItemEntity | None:
    if id_ not in _data:
        return None

    _data[id_].info = info

    return _data[id_]


def patch(id_: int, patch_info: PatchItemInfo) -> ItemEntity | None:
    if id_ not in _data:
        return None

    if _data[id_].deleted:
        return None

    if patch_info.name is not None:
        _data[id_].info.name = patch_info.name
    if patch_info.price is not None:
        _data[id_].info.price = patch_info.price

    cart_store.update_item_info(id_, _data[id_].info, patch_info)

    return _data[id_]
