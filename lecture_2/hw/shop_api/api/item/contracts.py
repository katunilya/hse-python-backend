from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

from .entities import (
    ItemInfo,
    ItemEntity,
    PatchItemInfo,
)


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


class ItemRequest(BaseModel):
    name: str
    price: float
    deleted: bool = False

    def as_item_info(self) -> ItemInfo:
        return ItemInfo(
            name=self.name,
            price=self.price,
            deleted=self.deleted,
        )


class PatchItemRequest(BaseModel):
    name: Optional[str] = Field(None, description="Name of the item")
    price: Optional[float] = Field(None, description="Price of the item")
    deleted: Optional[bool] = Field(None, description="Deleted status")

    model_config = ConfigDict(extra='forbid')

    def as_patch_item_info(self):
        return PatchItemInfo(
            name=self.name,
            price=self.price
        )