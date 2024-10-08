from pydantic import BaseModel
from typing import Optional

class ItemRequest(BaseModel):
    name: str
    price: float

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool

class ItemPatchRequest(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    model_config = ConfigDict(extra="forbid")