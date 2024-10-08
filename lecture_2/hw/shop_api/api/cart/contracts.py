from pydantic import BaseModel
from typing import List

# Модель для отдельного товара в корзине
class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

# Модель ответа на запрос корзины
class CartResponse(BaseModel):
    id: int
    items: List[CartItem]  # Список объектов CartItem
    price: float

    @staticmethod
    def from_entity(entity):
        return CartResponse(
            id=entity["id"],
            items=[CartItem(**item) for item in entity["items"]],
            price=entity["price"]
        )