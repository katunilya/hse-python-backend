from typing import List
from pydantic import BaseModel


class ItemInCart(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool


class CartInfo(BaseModel):
    items: List[ItemInCart]
    price: float


class CartEntity(BaseModel):
    id: int
    info: CartInfo


class PatchCartInfo(BaseModel):
    items: List[ItemInCart] | None = None
    price: float | None = None
