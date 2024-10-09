from typing import List
from pydantic import BaseModel


DEFAULT_ITEM_DTO_FIELDS = ["name", "price"]

class Item(BaseModel):
    """
    Модель товара в системе.
    
    Attributes:
        id (int): Идентификатор товара.
        name (str): Название товара.
        price (float): Цена товара.
        deleted (bool): Статус удалён ли товар (по умолчанию False).
    """
    id: int
    name: str
    price: float
    deleted: bool = False


class ItemDto(BaseModel):
    """
    Модель для передачи данных о товаре без идентификатора и флага deleted.
    
    Attributes:
        name (str): Название товара.
        price (float): Цена товара.
    """
    name: str
    price: float


class ItemCart(BaseModel):
    """
    Модель товара в корзине.
    
    Attributes:
        id (int): Идентификатор товара.
        name (str): Название товара.
        quantity (int): Количество товара в корзине.
        available (bool): Доступность товара (удален или нет).
    """
    id: int
    name: str
    quantity: int
    available: bool


class Cart(BaseModel):
    """
    Модель корзины.
    
    Attributes:
        id (int): Идентификатор корзины.
        items (List[ItemCart]): Список товаров в корзине.
        price (float): Общая стоимость товаров в корзине.
    """
    id: int
    items: List[ItemCart] = []
    price: float = 0.0
