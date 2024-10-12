from __future__ import annotations

from pydantic import BaseModel, ConfigDict
from typing import List

from .entities import (
    ItemInCart,
    CartEntity,
    CartInfo,
    PatchCartInfo,
)


class CartResponse(BaseModel):
    id: int
    items: List[ItemInCart]
    price: float

    @staticmethod
    def from_entity(entity: CartEntity) -> CartResponse:
        return CartResponse(
            id=entity.id,
            items=entity.info.items,
            price=entity.info.price,
        )


class CartRequest(BaseModel):
    items: List[ItemInCart]
    price: float

    def as_cart_info(self) -> CartInfo:
        return CartInfo(
            items=self.items,
            price=self.price,
        )


class PatchCartRequest(BaseModel):
    items: List[ItemInCart] | None = None
    price: float | None = None

    model_config = ConfigDict(extra='forbid')

    def as_patch_cart_info(self) -> PatchCartInfo:
        return PatchCartInfo(
            items=self.items,
            price=self.price,
        )