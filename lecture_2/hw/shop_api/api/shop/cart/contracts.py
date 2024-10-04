from __future__ import annotations
from pydantic import BaseModel

from lecture_2.hw.shop_api.store.cart_store.models import (
    CartEntity,
    ItemsInCartInfo,
)


class ItemInCartResponse(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

    @staticmethod
    def from_item_in_cart_info(info: ItemsInCartInfo) -> ItemInCartResponse:
        return ItemInCartResponse(
            id=info.id_,
            name=info.name,
            quantity=info.quantity,
            available=info.available,
        )


class CartResponse(BaseModel):
    id: int
    items: list[ItemInCartResponse]
    price: float

    @staticmethod
    def from_entity(entity: CartEntity) -> CartResponse:
        return CartResponse(
            id=entity.id_,
            price=entity.info.price,
            items=[
                ItemInCartResponse.from_item_in_cart_info(info)
                for info in entity.info.items.values()
            ],
        )
