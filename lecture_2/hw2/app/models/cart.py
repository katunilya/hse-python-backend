from pydantic import BaseModel, Field
from typing import List

   class CartItem(BaseModel):
       id: int
       name: str
       quantity: int
       available: bool

   class Cart(BaseModel):
       id: int = Field(default=None)
       items: List[CartItem] = []
       price: float = 0.0