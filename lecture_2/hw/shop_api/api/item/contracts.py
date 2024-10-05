from pydantic import BaseModel, ConfigDict
from typing import Optional


class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False


class ItemRequest(BaseModel):
    name: str
    price: float


class ItemPatchRequest(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

    model_config = ConfigDict(extra="forbid")
