from statistics import quantiles
from pydantic import BaseModel, Field
from typing import Optional
        
class Item(BaseModel):
    name:str
    price:float
    
class CartItem(Item):
    id:int
    deleted:bool
    cart_id: Optional[int]
    quantity: Optional[int]
    
class Cart(BaseModel):
    id:int
    items:list[CartItem]
    price:float

class EmptyItem(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None