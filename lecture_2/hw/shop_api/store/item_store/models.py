from dataclasses import dataclass


@dataclass(slots=True)
class ItemInfo:
    name: str
    price: float


@dataclass(slots=True)
class ItemEntity:
    id_: int
    info: ItemInfo
    deleted: bool


@dataclass(slots=True)
class PatchItemInfo:
    name: str
    price: float
