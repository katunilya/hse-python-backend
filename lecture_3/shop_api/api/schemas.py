from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, PositiveFloat, NonNegativeFloat

from ..shop.models import (
    CartItem,
    Cart,
    Item,
    ItemInfo,
    PatchItemInfo,
)


class CartResponse(BaseModel):
    id: int
    items: List[CartItem]
    price: NonNegativeFloat

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
    deleted: bool = False

    def as_item_info(self) -> ItemInfo:
        return ItemInfo(
            name=self.name,
            price=self.price,
            deleted=self.deleted,
        )


class PatchItemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = None
    price: Optional[PositiveFloat] = None

    def as_patch_item_info(self) -> PatchItemInfo:
        return PatchItemInfo(name=self.name, price=self.price)
