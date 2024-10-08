from pydantic import BaseModel, Field
from typing import Optional


class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = Field(default=False)


class ItemCreate(BaseModel):
    name: str
    price: float

    model_config = {
        "extra": "forbid"
    }


class ItemPut(BaseModel):
    name: str
    price: float
    deleted: bool = Field(default=False)

    model_config = {
        "extra": "forbid"
    }


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

    model_config = {
        "extra": "forbid"
    }
