from pydantic import BaseModel
from typing import List


class ItemBase(BaseModel):
    name: str
    price: float


class ItemCreate(ItemBase):
    pass


class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool

    class Config:
        from_attributes = True


class CartItemBase(BaseModel):
    item_id: int
    quantity: int


class CartItemCreate(CartItemBase):
    pass


class CartItem(BaseModel):
    id: int
    item_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


class CartBase(BaseModel):
    price: float


class CartCreate(CartBase):
    pass


class Cart(BaseModel):
    id: int
    items: List[CartItem] = []
    price: float

    class Config:
        from_attributes = True