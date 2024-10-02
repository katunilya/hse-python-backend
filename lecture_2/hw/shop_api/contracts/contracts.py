from __future__ import annotations

from pydantic import BaseModel

from lecture_2.hw.shop_api.db.models import CartItem, Cart, Item


class ItemInCartRequest(BaseModel):
    id: int = 0
    name: str = "default name"
    quantity: int = 0
    available: bool = True

    def asCartItem(self):
        return CartItem(
            id=self.id,
            name=self.name,
            quantity=self.quantity,
            available=self.available
        )


class CartRequest(BaseModel):
    id: int = 0
    items: list[ItemInCartRequest] = None
    price: float = 0.0

    def asCart(self):
        return Cart(
            id=self.id,
            items=[item.asCartItem() for item in self.items],
            price=self.price
        )


class ItemRequest(BaseModel):
    id: int = 0
    name: str
    price: float = 0.0
    deleted: bool = False

    class Config:
        extra = "forbid"

    def asItem(self):
        return Item(
            id=self.id,
            name=self.name,
            price=self.price,
            deleted=self.deleted
        )
