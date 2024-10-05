from dataclasses import dataclass
from collections import defaultdict


@dataclass(slots=True)
class ItemInfo:
    name: str
    price: float
    deleted: bool


@dataclass(slots=True)
class PatchItemInfo:
    name: str | None = None
    price: float | None = None


@dataclass(slots=True)
class ItemEntity:
    id: int
    info: ItemInfo


@dataclass(slots=True)
class CartInfo:
    items: defaultdict[int, int]


@dataclass(slots=True)
class CarEntity:
    id: int
    info: CartInfo
