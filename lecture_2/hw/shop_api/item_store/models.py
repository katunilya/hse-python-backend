from dataclasses import dataclass


@dataclass(slots=True)
class ItemInfo:
    id_: int
    name: str
    price: float
    deleted: bool


@dataclass(slots=True)
class PatchItemInfo:
    deleted: bool
