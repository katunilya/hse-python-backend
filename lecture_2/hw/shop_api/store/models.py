from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ItemInfo:
    name: str
    price: float
    deleted: bool


@dataclass
class PatchItemInfo:
    name: str | None
    price: float | None


@dataclass
class ItemEntity:
    id: int
    info: ItemInfo


@dataclass
class CartInfo:
    items: defaultdict = field(default_factory=lambda: defaultdict(int))


@dataclass
class CartItemEntity:
    id: int
    name: str
    quantity: int
    avaliable: bool


@dataclass
class CartEntity:
    id: int
    price: float
    items: list[CartItemEntity]
