from pydantic import BaseModel

class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False