from dataclasses import dataclass


@dataclass(slots=True)
class ItemsInCartInfo:
    id_: int
    name: str
    quantity: int
    available: bool


@dataclass(slots=True)
class CartInfo:
    id_: int
    items: dict[int, ItemsInCartInfo]
    price: float


@dataclass(slots=True)
class CartEntity:
    id_: int
    info: CartInfo
