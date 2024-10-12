from typing import List

from pydantic import BaseModel

class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False

DEFAULT_ITEM_DTO_FIELDS = ["name", "price"]

class ItemDto(BaseModel):
    name: str
    price: float


class ItemCart(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

class Cart(BaseModel):
    id: int
    items: List[ItemCart] = []
    price: float = 0.0
