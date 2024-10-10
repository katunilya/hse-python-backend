from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False

class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool = True

class Cart(BaseModel):
    id: int
    items: List[CartItem] = []
    price: float = 0.0

class ItemPost(BaseModel):
    name: str
    price: float

class ItemPatch(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

    model_config = ConfigDict(extra='forbid')  # Запрещаем дополнительные поля
