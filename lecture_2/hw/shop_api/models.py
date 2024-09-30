from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional

class ItemInCart(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool = True

class Cart(BaseModel):
    id: int
    items: List[ItemInCart] = Field(default_factory=list)
    price: float = 0.0

class Item(BaseModel):
    id: Optional[int] = None
    name: str
    price: float = 0.0
    deleted: bool = False

class ItemPut(BaseModel):
    name: str
    price: float = 0.0
    deleted: bool = False

class ItemPatch(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

    model_config = ConfigDict(extra='forbid')