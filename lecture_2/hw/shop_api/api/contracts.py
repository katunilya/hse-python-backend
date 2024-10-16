from __future__ import annotations
from pydantic import BaseModel, ConfigDict

from typing import List, Optional
from lecture_2.hw.shop_api.store import CartItem


class CartResponse(BaseModel):
    id: int
    items: List[CartItem]
    price: float

class ItemPatchRequest(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    deleted: bool = False

    model_config = ConfigDict(extra="forbid")

class ItemRequest(BaseModel):
    name: str
    price: float
