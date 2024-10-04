from __future__ import annotations
from pydantic import BaseModel, ConfigDict

from lecture_2.hw.shop_api.store.item_store.models import ItemInfo, PatchItemInfo, ItemEntity


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool

    @staticmethod
    def from_entity(entity: ItemEntity) -> ItemResponse:
        return ItemResponse(
            id=entity.id_,
            name=entity.info.name,
            price=entity.info.price,
            deleted=entity.deleted,
        )


class ItemRequest(BaseModel):
    name: str
    price: float

    def as_item_info(self) -> ItemInfo:
        return ItemInfo(name=self.name, price=self.price)


class PatchItemRequest(BaseModel):
    name: str | None = None
    price: float | None = None

    model_config = ConfigDict(extra="forbid")

    def as_patch_item_info(self) -> PatchItemInfo:
        return PatchItemInfo(name=self.name, price=self.price)
