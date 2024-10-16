from typing import Optional
from pydantic import BaseModel, ConfigDict

class InitItem(BaseModel):
    price: float
    name: str
    deleted: bool = False
    model_config = ConfigDict(extra="forbid")
    
class Item(BaseModel):
    id: int
    item: InitItem 

class ItemPatch(BaseModel):
    price: Optional[float] = None
    name: Optional[str] = None
    model_config = ConfigDict(extra="forbid")
