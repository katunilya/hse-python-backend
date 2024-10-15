from pydantic import BaseModel, NonNegativeFloat, NonNegativeInt
from typing import List
from lecture_2.hw.shop_api.api.store.models import *

class CartItem(BaseModel):
    id: int
    name: str
    quantity: NonNegativeInt
    available: bool

    def from_entity(entity: CartItem) -> 'CartItem':
        return CartItem(
            id = entity.id,
            name = entity.name,
            quantity = entity.quantity,
            available = entity.available
        )

class CartResponse(BaseModel):
    id: int
    items: List[CartItem]
    price: NonNegativeFloat

    def from_entity(entity: Cart) -> 'CartResponse':
        return CartResponse(
            id = entity.id,
            items = entity.items,
            price = entity.price
        )

class CartRequest(BaseModel):
    item_id: int

    def as_item_info(self) -> Cart:
        return Cart(
            id = self.id,
            items = self.items,
            price = self.price,
        )