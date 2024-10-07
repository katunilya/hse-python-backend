from pydantic import BaseModel

class ItemDto(BaseModel):
    name: str
    price: float

class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False