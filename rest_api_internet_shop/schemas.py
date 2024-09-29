from pydantic import BaseModel
from typing import List

class ItemSchema(BaseModel):
    name: str
    price: float

class CartSchema(BaseModel):
    id: int
    items: List[ItemSchema] = []
    price: float
