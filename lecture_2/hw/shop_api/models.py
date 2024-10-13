from pydantic import BaseModel
from typing import List, Optional

class Item(BaseModel):
    id: int = None
    name: str
    price: float
    deleted: bool = False

class CartItem(BaseModel):
    id: int = None
    name: str
    quantity: int
    available: bool = True

class Cart(BaseModel):
    id: int = None
    items: List[CartItem] = []
    price: float = 0.0
