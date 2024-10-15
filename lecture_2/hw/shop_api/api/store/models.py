from dataclasses import dataclass, field
from typing import List
from pydantic import NonNegativeFloat, NonNegativeInt

# товар в корзине
@dataclass(slots=True)
class CartItem:
    id: int                                                 # id товара
    name: str                                               # название
    quantity: NonNegativeInt                                # количество товара в корзине
    available: bool                                         # доступность (не удалён ли товар)

# корзина
@dataclass(slots=True)
class Cart:
    id: int                                                 # id корзины
    items: List[CartItem] = field(default_factory=list)     # список товаров в корзине
    price: NonNegativeFloat = 0.0                           # общая сумма заказа

# товар
@dataclass(slots=True)
class Item:
    id: int                                                 # id товара
    name: str                                               # название товара
    price: NonNegativeFloat                                 # цена товара
    deleted: bool = False                                   # удалён ли товар

@dataclass(slots=True)
class ItemPatchInfo:
    name: str = None,
    price: NonNegativeFloat = None