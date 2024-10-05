from dataclasses import dataclass, field
from typing import List

@dataclass(slots=True)
class CartItem:
    id: int
    name: str
    quantity: int
    available: bool

@dataclass(slots=True)
class Cart:
    id: int
    items: List[CartItem] = field(default_factory=list)
    price: float = 0.0

@dataclass(slots=True)
class Item:
    id: int
    name: str
    price: float
    deleted: bool = False
