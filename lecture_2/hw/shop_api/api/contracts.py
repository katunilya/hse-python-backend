from __future__ import annotations


from lecture_2.hw.shop_api.store.models import (
    CartEntity,
    CartItemEntity,
    ItemInfo,
    ItemEntity,
    PatchItemInfo,
)
from pydantic import BaseModel, ConfigDict


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool

    @staticmethod
    def from_entity(entity: ItemEntity) -> ItemResponse:
        return ItemResponse(
            id=entity.id,
            name=entity.info.name,
            price=entity.info.price,
            deleted=entity.info.deleted,
        )


class CartItemResponse(BaseModel):
    id: int
    name: str
    quantity: int
    avaliable: bool

    @staticmethod
    def from_entity(entity: CartItemEntity) -> CartItemResponse:
        return CartItemResponse(
            id=entity.id,
            name=entity.name,
            quantity=entity.quantity,
            avaliable=entity.avaliable,
        )


class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse]
    price: float

    @staticmethod
    def from_entity(entity: CartEntity) -> CartResponse:
        return CartResponse(
            id=entity.id,
            items=[CartItemResponse.from_entity(ent) for ent in entity.items],
            price=entity.price,
        )


class ItemRequest(BaseModel):
    name: str
    price: float

    def as_item_info(self) -> ItemInfo:
        return ItemInfo(name=self.name, price=self.price, deleted=False)


class PatchItemRequest(BaseModel):
    name: str | None = None
    price: float | None = None

    model_config = ConfigDict(extra="forbid")

    def as_patch_item_info(self) -> PatchItemInfo:
        return PatchItemInfo(name=self.name, price=self.price)
