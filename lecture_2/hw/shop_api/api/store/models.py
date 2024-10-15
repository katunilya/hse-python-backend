from dataclasses import dataclass, field
from typing import List

# товар в корзине
@dataclass(slots=True)
class CartItem:
    id: int                                                 # id товара
    name: str                                               # название
    quantity: int                                           # количество товара в корзине
    available: bool                                         # доступность (не удалён ли товар)

# корзина
@dataclass(slots=True)
class Cart:
    id: int                                                 # id корзины
    items: List[CartItem] = field(default_factory=list)     # список товаров в корзине
    price: float = 0.0                                      # общая сумма заказа

# товар
@dataclass(slots=True)
class Item:
    id: int                                                 # id товара
    name: str                                               # название товара
    price: float                                            # цена товара
    deleted: bool = False                                   # удалён ли товар