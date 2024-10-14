from dataclasses import dataclass, field
from typing import List


@dataclass(slots=True)
class Item:
    id: int
    name: str
    price: float
    deleted: bool = False

    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "deleted": self.deleted,
        }


@dataclass(slots=True)
class CartItem:
    id: int
    item_id: int
    name: str
    quantity: int
    available: bool

    def dict(self):
        return {
            "id": self.id,
            "item_id": self.item_id,
            "name": self.name,
            "quantity": self.quantity,
            "available": self.available,
        }


@dataclass(slots=True)
class Cart:
    id: int
    items: List[CartItem] = field(default_factory=list)
    price: float = 0.0

    def dict(self):
        return {
            "id": self.id,
            "items": [item.dict() for item in self.items],
            "price": self.price,
        }
