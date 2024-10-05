import copy

from typing import Iterable

from .entities import *
from lecture_2.hw.shop_api.api.storages import (
    item_data, item_id_generator
)

def add(info: ItemInfo) -> ItemEntity:
    _id = next(item_id_generator)
    item_data[_id] = info

    return ItemEntity(id=_id, info=info)


def get_one_item(_id: int) -> ItemEntity:
    item = ItemEntity(
        id=_id,
        info=item_data.get(_id, None)
    )
    if not item:
        return None
    return item


def get_many(
        offset: int = 0,
        limit: int = 10,
        min_price: float | None = None,
        max_price: float | None = None,
        show_deleted: bool = None,
) -> Iterable[ItemEntity]:
    _filtered_data = {
        info_id: info for info_id, info in item_data.items() if
        (min_price is None or info.price >= min_price) and
        (max_price is None or info.price <= max_price) and
        (show_deleted or not info.deleted)
    }
    curr = 0
    for id, info in _filtered_data.items():
        if offset <= curr < offset + limit:
            yield ItemEntity(id=id, info=info)
        curr += 1


def put_item_by_id(_id: int, info: ItemInfo):
    print("Начинаем put")
    if _id not in item_data:
        print("Не нашли")
        return None
    item_data[_id] = info
    print("Замена прошла успешно")
    return ItemEntity(id=_id, info=info)


def patch_item_by_id(_id: int, info: PatchItemInfo) -> ItemEntity:
    if _id not in item_data:
        return None 
    update_dict = info.model_dump(exclude_unset=True)

    if "deleted" in update_dict:
        return None

    item_data[_id] = item_data[_id].model_copy(update=update_dict)
    return ItemEntity(id=_id, info=item_data[_id])


def delete_item_by_id(_id) -> ItemEntity:
    deleted_item = item_data.pop(_id)
    return ItemEntity(id=_id, info=deleted_item)