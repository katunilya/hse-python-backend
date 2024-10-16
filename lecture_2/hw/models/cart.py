from dataclasses import Field, dataclass, field
from typing import List

from pydantic import BaseModel, ConfigDict
from lecture_2.hw.models.item import *

class ItemInCart(BaseModel):
    id: int
    name: str
    deleted: bool
    quantity: int
    model_config = ConfigDict(extra="forbid")
    
class Cart(BaseModel):
    id : int
    items: List[ItemInCart] = field(default_factory=list)
    price: float
    model_config = ConfigDict(extra="forbid")