from pydantic import BaseModel, ConfigDict
from typing import List

class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

class Cart(BaseModel):
    id: int
    items: List[CartItem]
    price: float
    total_quantity: int

class Item(BaseModel):  
    id: int
    name: str
    price: float
    deleted: bool = False

class ItemPost(BaseModel):
    name: str = None
    price: float = None
    model_config = ConfigDict(extra="forbid")
