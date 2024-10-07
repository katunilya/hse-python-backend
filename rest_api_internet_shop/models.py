from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict

class ItemCreate(BaseModel):
    name: str
    price: float = Field(gt=0.0)

    model_config = ConfigDict(extra="forbid")


class ItemUpdate(BaseModel):
    name: str
    price: float = Field(gt=0.0)

    model_config = ConfigDict(extra="forbid")


class ItemPatch(BaseModel):
    name: str | None = None
    price: float | None = Field(None, gt=0.0)

    model_config = ConfigDict(extra="forbid")


class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False


class CartItem(BaseModel):
    id: int  
    name: str | None = None
    quantity: int = 1
    available: bool = True


class Cart(BaseModel):
    id: int
    items: List[CartItem] = []

    def update_item_availability(self, items_db: Dict[int, Item]):
        for cart_item in self.items:
            item = items_db.get(cart_item.id)
            if item and not item.deleted:
                cart_item.available = True
                cart_item.name = item.name
            else:
                cart_item.available = False
                cart_item.name = None

    def calculate_totals(self, items_db: Dict[int, Item]):
        self.price = sum(
            items_db[item.id].price * item.quantity
            for item in self.items
            if items_db.get(item.id) and not items_db[item.id].deleted
        )
        self.quantity = sum(
            item.quantity
            for item in self.items
            if items_db.get(item.id) and not items_db[item.id].deleted
        )


class CartResponse(Cart):
    price: float = 0.0
    quantity: int = 0
