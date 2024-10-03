from __future__ import annotations
from pydantic import BaseModel, ConfigDict

from lecture_2.hw.shop_api.item_store.models import ItemInfo, PatchItemInfo


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool

    @staticmethod
    def from_info(info: ItemInfo) -> ItemResponse:
        return ItemResponse(
            id=info.id_, name=info.name, price=info.price, deleted=info.deleted
        )


class ItemRequest(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool

    def as_item_info(self) -> ItemInfo:
        return ItemInfo(
            id_=self.id, name=self.name, price=self.price, deleted=self.deleted
        )


class PatchItemRequest(BaseModel):
    deleted: bool

    model_config = ConfigDict(extra="forbid")

    def as_patch_item_info(self) -> PatchItemInfo:
        return PatchItemInfo(deleted=self.deleted)
