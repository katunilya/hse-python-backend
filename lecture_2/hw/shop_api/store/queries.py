from typing import Iterable, Callable

from lecture_2.hw.shop_api.store.models import (
    ItemInfo,
    PatchItemInfo,
    CartInfo
)
from lecture_2.hw.shop_api.contracts import (
    ItemEntity,
    CarEntity
)

_items = dict[int, ItemInfo]()
_carts = dict[int, CartInfo]()


def int_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1


def item_constraint(show_deleted: bool) -> list[Callable]:
    return [lambda x: True if show_deleted else not x.deleted]


def cart_constraint(min_quantity: int, max_quantity: int | None) -> list[Callable]:
    return [lambda x: min_quantity <= sum(x.items.values()) and
                      (sum(x.items.values()) <= max_quantity if max_quantity is not None else True)]


_items_id_generator = int_id_generator()
_carts_id_generator = int_id_generator()

objects_mapping = {
    "item": (_items_id_generator, _items, ItemEntity, item_constraint),
    "cart": (_carts_id_generator, _carts, CarEntity, cart_constraint)
}


def add(object_type: str, info):
    gen, data, entity, _ = objects_mapping[object_type]
    _id = next(gen)
    data[_id] = info
    return entity(_id, info)


def add_to_cart(cart_entity: CarEntity, item_id: int):
    cart_entity.info.items[item_id] += 1


def delete(id: int) -> None:
    _, data, *_ = objects_mapping["item"]
    if id in data:
        data[id].deleted = True


def check_published(object_type: str, obj_info):
    if object_type == "item":
        return not obj_info.deleted
    else:
        return True


def get_one(object_type: str, id: int):
    _, data, entity, _ = objects_mapping[object_type]
    if id not in data:
        return None
    if not check_published(object_type, obj_info := data[id]):
        return None
    return entity(id=id, info=obj_info)


def get_many(object_type: str, constraint_data,
             offset: int = 0, limit: int = 10,
             min_price: float = 0, max_price: float = float("+inf")) -> Iterable:
    from itertools import islice
    _, data, entity, constraint_maker = objects_mapping[object_type]
    count = 0

    def get_price(object_type: str, obj) -> float:
        if object_type == "item":
            return obj.price
        else:
            return sum([get_one("item", k).info.price * v for k, v in obj.items.items()])

    for id, info in filter(
            lambda val: all([
                all(map(lambda x: x(val[1]), constraint_maker(*constraint_data))),
                min_price <= get_price(object_type, val[1]) <= max_price,
            ]),
            islice(data.items(), offset, None)):
        count += 1
        yield entity(id, info)
        if count == limit:
            break


def put(id: int, info: ItemInfo) -> ItemEntity | None:
    _, data, *_ = objects_mapping["item"]
    if id not in data:
        return None
    data[id] = info
    return ItemEntity(id=id, info=info)


def patch(id: int, patch_info: PatchItemInfo) -> ItemEntity | None:
    _, data, *_ = objects_mapping["item"]

    if id not in data:
        return None

    if data[id].deleted:
        return None

    if patch_info.name is not None:
        data[id].name = patch_info.name

    if patch_info.price is not None:
        data[id].price = patch_info.price

    return ItemEntity(id=id, info=data[id])
