from __future__ import annotations
from pydantic import BaseModel, ConfigDict

from lecture_2.hw.shop_api.models import (
    Item,
    ItemInfo,
    PatchItemInfo,
    ItemInCart,
    ItemInCartForResponse,
    Cart,
)


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float

    @staticmethod
    def from_item(item: Item) -> ItemResponse:
        return ItemResponse(
            id=item.id,
            name=item.info.name,
            price=item.info.price,
        )


class ItemRequest(BaseModel):
    name: str
    price: float

    def to_item_info(self) -> ItemInfo:
        return ItemInfo(name=self.name, price=self.price)


class PutItemRequest(BaseModel):
    name: str
    price: float
    deleted: bool | None = None

    model_config = ConfigDict(extra="forbid")

    def to_item_info(self) -> ItemInfo:
        return ItemInfo(name=self.name, price=self.price, deleted=self.deleted)


class PatchItemRequest(BaseModel):
    name: str | None = None
    price: float | None = None

    model_config = ConfigDict(extra="forbid")

    def to_item_info(self) -> PatchItemInfo:
        return PatchItemInfo(name=self.name, price=self.price)


class CartResponse(BaseModel):
    id: int
    items: list[ItemInCartForResponse]
    price: float

    @staticmethod
    def from_cart(cart: Cart) -> CartResponse:
        cart_items_for_response = []
        for item_id, item in cart.items.items():
            cart_items_for_response.append(
                ItemInCartForResponse(item_id, item.name, item.quantity, item.available)
            )

        return CartResponse(
            id=cart.id,
            items=cart_items_for_response,
            price=cart.price,
        )


class CartAddRequest(BaseModel):
    cart_id: int
    item_id: int
