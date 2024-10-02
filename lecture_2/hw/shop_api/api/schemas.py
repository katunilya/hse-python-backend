from __future__ import annotations

from typing import List
from pydantic import BaseModel, PositiveFloat

from lecture_2.hw.shop_api.shop.models import (
    CartItem,
    Cart,
    Item,
    ItemInfo,
    PatchItemInfo,
)


class CartResponse(BaseModel):
    id: int
    items: List[CartItem]
    price: PositiveFloat

    @staticmethod
    def from_entity(entity: Cart) -> CartResponse:
        return CartResponse(
            id=entity.id,
            items=entity.items,
            price=entity.price,
        )


class ItemResponse(BaseModel):
    id: int
    name: str
    price: PositiveFloat
    deleted: bool

    @staticmethod
    def from_entity(entity: Item) -> ItemResponse:
        return ItemResponse(
            id=entity.id,
            name=entity.info.name,
            price=entity.info.price,
            deleted=entity.info.deleted,
        )


class ItemRequest(BaseModel):
    name: str
    price: PositiveFloat
    deleted: bool

    def as_item_info(self) -> ItemInfo:
        return ItemInfo(
            name=self.name,
            price=self.price,
            deleted=self.deleted,
        )


class PatchItemRequest(BaseModel):
    name: str
    price: PositiveFloat

    def as_patch_item_info(self) -> PatchItemInfo:
        return PatchItemInfo(name=self.name, price=self.price)
