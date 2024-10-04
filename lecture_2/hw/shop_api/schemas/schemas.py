from pydantic import BaseModel
from typing import List

class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

    class Config:
        orm_mode = True
        

class Cart(BaseModel):
    id: int
    items: List[CartItem]
    price: float

    class Config:
        orm_mode = True

class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False
    
    class Config:
        orm_mode = True