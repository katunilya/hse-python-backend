from dataclasses import dataclass, field

from typing import List

@dataclass(slots=True)
class ItemEntity:
    id: int
    name: str
    price: float
    deleted: bool = False

@dataclass(slots=True)
class ItemInCart:
    id: int
    name: str
    quantity: int
    available: bool

@dataclass(slots=True)
class CartEntity:
    id: int
    items: List[ItemInCart] = field(default_factory=list)
    price: float = 0.0
    quantity: int = 0


