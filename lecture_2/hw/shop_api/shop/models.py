from dataclasses import dataclass, field
from typing import List


@dataclass
class ItemInfo:
    name: str
    price: float
    deleted: bool = False


@dataclass
class Item:
    id: int
    info: ItemInfo


@dataclass
class PatchItemInfo:
    name: str
    price: float


@dataclass
class CartItem:
    item: Item
    quantity: int
    available: bool = True


@dataclass
class Cart:
    id: int
    items: list = field(default_factory=lambda: [])
    price: float = 0.0
