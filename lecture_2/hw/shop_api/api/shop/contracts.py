from pydantic import BaseModel
from __future__ import annotations

from lecture_2.hw.shop_api.store.models import ItemInfo


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool

    @staticmethod
    def from_info(info: ItemInfo) -> ItemResponse:
        return ItemResponse(
            id=info.id_,
            name=info.name,
            price=info.price,
            deleted=info.deleted
        )

class ItemRequest(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool

    def as_item_info(self) -> ItemInfo:
        return ItemInfo(
            id_=self.id,
            name=self.name,
            price=self.price,
            deleted=self.deleted
        )