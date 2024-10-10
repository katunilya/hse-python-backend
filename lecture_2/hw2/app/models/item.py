from pydantic import BaseModel, Field
from typing import Optional

   class Item(BaseModel):
       id: int = Field(default=None)
       name: str
       price: float
       deleted: bool = False

   class ItemCreate(BaseModel):
       name: str
       price: float

   class ItemUpdate(BaseModel):
       name: Optional[str]
       price: Optional[float]