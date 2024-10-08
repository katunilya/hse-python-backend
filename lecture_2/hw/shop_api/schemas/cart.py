from pydantic import BaseModel
from typing import List, Optional


class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool


class Cart(BaseModel):
    id: int
    items: Optional[List[CartItem]] = None
    price: Optional[float] = None


class CartCreate(BaseModel):
    id: int
    items: Optional[List[CartItem]] = None
    price: Optional[float] = None

    model_config = {
        "extra": "forbid"
    }
