from pydantic import BaseModel

class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False

class Cart(BaseModel):
    id: int
    items: list
    price: float