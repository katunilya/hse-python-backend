from dataclasses import field

from typing import List

from pydantic import BaseModel

from lecture_2.hw.shop_api.store.models import (
    CartEntity, ItemInCart,
)

class CartResponse(BaseModel):
    id: int
    items: List[ItemInCart] = field(default_factory=list)
    price: float = 0.0
    quantity: int = 0

    @staticmethod
    def from_entity(entity: CartEntity):
        return CartResponse(id=entity.id, items=entity.items, price=entity.price, quantity=entity.quantity)


class CartRequest(BaseModel):
    id: int

