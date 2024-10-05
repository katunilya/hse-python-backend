from pydantic import BaseModel, ConfigDict
from collections import defaultdict

from lecture_2.hw.shop_api.store.models import (
    ItemEntity,
    ItemInfo,
    PatchItemInfo,
    CarEntity,
    CartInfo
)

from lecture_2.hw.shop_api import store


# from lecture_2.hw.shop_api.store import get_one


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool

    @staticmethod
    def from_entity(entity: ItemEntity):
        return ItemResponse(
            id=entity.id,
            name=entity.info.name,
            price=entity.info.price,
            deleted=entity.info.deleted
        )


class ItemRequest(BaseModel):
    name: str
    price: float
    deleted: bool = False

    def as_info(self) -> ItemInfo:
        return ItemInfo(
            name=self.name,
            price=self.price,
            deleted=self.deleted
        )


class PatchItemRequest(BaseModel):
    name: str | None = None
    price: float | None = None

    model_config = ConfigDict(extra="forbid")

    def as_patch_item_info(self) -> PatchItemInfo:
        return PatchItemInfo(name=self.name, price=self.price)


class ItemResponseInCart(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool


class CartResponse(BaseModel):
    id: int
    items: list[ItemResponseInCart]
    price: float = 0

    @staticmethod
    def from_entity(entity: CarEntity):
        price = 0

        def ItemResp_from_key(item_id: int, amount: int) -> ItemResponseInCart:
            nonlocal price
            item: ItemEntity = store.get_one("item", item_id)
            price += amount * item.info.price
            return ItemResponseInCart(
                id=item.id,
                name=item.info.name,
                quantity=amount,
                available=(not item.info.deleted)
            )

        return CartResponse(
            id=entity.id,
            items=[ItemResp_from_key(k, c) for k, c in entity.info.items.items()],
            price=price,
        )


class CartRequest(BaseModel):

    def as_info(self) -> CartInfo:
        return CartInfo(items=defaultdict(int))
