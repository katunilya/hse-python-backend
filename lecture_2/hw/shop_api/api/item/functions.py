from typing import Iterable

from fastapi import HTTPException
from http import HTTPStatus

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
    if _id not in item_data:
        return None
    item_data[_id] = info
    return ItemEntity(id=_id, info=info)


def patch_item_by_id(id: int, info: PatchItemInfo) -> ItemEntity:
    if "deleted" in info.model_dump(exclude_none=True):
        print("ПЕРЕДАЛИ DELETED")
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=f"tryed to change deleted"
        )
    if id not in item_data:
        raise HTTPException(
            status_code=HTTPStatus.NOT_MODIFIED,
            detail=f"Item with id {id} not found"
        )
    entity = get_one_item(id)
    if entity.info.deleted:
        raise HTTPException(
            status_code=HTTPStatus.NOT_MODIFIED,
            detail="Cannot modify a deleted item"
        )
    updated_info = entity.info.model_copy(update=info.model_dump(exclude_unset=True))
    updated_entity = put_item_by_id(id, updated_info)
    return updated_entity


def delete_item_by_id(_id) -> ItemEntity:
    if _id not in item_data:
        raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail=f"Item with id {id} not found"
        )
    
    # if item_data[_id].deleted:
    #     raise HTTPException(
    #     status_code=HTTPStatus.NOT_FOUND,
    #     detail=f"Item with id {id} not found"
    #     )
    
    item_data[_id].deleted = True
    deleted_item = item_data[_id]

    return ItemEntity(id=_id, info=deleted_item)
