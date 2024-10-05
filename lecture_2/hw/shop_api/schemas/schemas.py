from pydantic import BaseModel
from typing import List, Optional

class ItemBase(BaseModel):
    name: str
    price: float

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

class ItemResponse(ItemBase):
    id: int
    deleted: bool

    class Config:
        orm_mode = True

class CartItemResponse(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

    class Config:
        orm_mode = True

class CartResponse(BaseModel):
    id: int
    items: List[CartItemResponse]
    price: float

    class Config:
        orm_mode = True
