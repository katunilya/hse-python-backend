from pydantic import BaseModel, ConfigDict, NonNegativeFloat
from typing import Optional
from lecture_2.hw.shop_api.api.store.models import *

class ItemRequest(BaseModel):
    name: str
    price: NonNegativeFloat
    
    def as_item_info(self) -> Item:
        return Item(
            id = self.id,
            name = self.name,
            price = self.price,
            deleted = self.deleted
        )

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool

    def from_entity(entity: Item) -> 'ItemResponse':
        return ItemResponse(
            id = entity.id,
            name = entity.name,
            price = entity.price,
            deleted = entity.deleted
        )

class ItemPatchRequest(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    model_config = ConfigDict(extra="forbid")

    def as_item_patch_info(self) -> ItemPatchInfo:
        return ItemPatchInfo(
            name = self.name,
            price = self.price
        )