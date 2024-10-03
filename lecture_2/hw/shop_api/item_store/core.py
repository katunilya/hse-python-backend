from typing import Iterable

from .models import ItemInfo, PatchItemInfo

_data = dict[int, ItemInfo]()


def add(info: ItemInfo) -> None:
    _data[info.id_] = info

def delete(id_: int) -> None:
    if id_ in _data:
        _data[id_].deleted = True


def get_one(id_: int) -> ItemInfo | None:
    if id_ not in _data:
        return None

    return _data[id_]


def get_many(
    offset: int = 0,
    limit: int = 10,
    min_price: float | None = None,
    max_price: float | None = None,
    show_deleted: bool = False,
) -> Iterable[ItemInfo]:
    filtered_items = _data.values()
    if min_price is not None:
        filtered_items = (item for item in filtered_items if item.price >= min_price)
    if max_price is not None:
        filtered_items = (item for item in filtered_items if item.price <= max_price)
    if not show_deleted:
        filtered_items = (item for item in filtered_items if not item.deleted)
    curr = 0
    for item in filtered_items:
        if offset <= curr < offset + limit:
            yield item

        curr += 1


def update(id_: int, info: ItemInfo) -> ItemInfo | None:
    if id_ not in _data:
        return None

    _data[id_] = info

    return info


def patch(id_: int, patch_info: PatchItemInfo) -> ItemInfo | None:
    if id_ not in _data:
        return None

    if patch_info.deleted is not None:
        _data[id_].deleted = patch_info.deleted

    return _data[id_]
