from typing import List
from pydantic import BaseModel


class ItemInfo(BaseModel):
    name: str
    price: float
    deleted: bool


class ItemEntity(BaseModel):
    id: int
    info: ItemInfo


class PatchItemInfo(BaseModel):
    name: str | None = None
    price: float | None = None
    deleted: bool | None = None