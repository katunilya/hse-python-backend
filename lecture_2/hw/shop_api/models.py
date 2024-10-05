from dataclasses import dataclass


@dataclass(slots=True)
class PatchItemInfo:
    name: str
    price: float


@dataclass(slots=True)
class ItemInfo:
    name: str
    price: float
    deleted: bool = False


@dataclass(slots=True)
class Item:
    id: int
    info: ItemInfo


@dataclass(slots=True)
class ItemInCart:
    name: str
    quantity: int
    available: bool

@dataclass(slots=True)
class ItemInCartForResponse:
    id: int
    name: str
    quantity: int
    available: bool


@dataclass(slots=True)
class Cart:
    id: int
    items: dict[int, ItemInCart]
    price: float
