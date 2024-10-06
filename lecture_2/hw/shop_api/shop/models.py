from dataclasses import dataclass, field
from typing import Optional


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
    name: Optional[str] = None
    price: Optional[float] = None


@dataclass
class CartItem:
    item: Item
    quantity: int
    available: bool = True


@dataclass
class Cart:
    id: int
    items: list[CartItem]
    price: float = 0.0
