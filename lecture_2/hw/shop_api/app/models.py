
from pydantic import BaseModel, confloat, conint
from typing import List, Optional

class UpdateItem(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    model_config = {'extra': 'forbid'}

class NewItem(BaseModel):
    name: str
    price: float

class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False

class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

class Cart(BaseModel):
    id: int
    items: List[CartItem] = []
    price: float = 0.0
