from __future__ import annotations
from pydantic import Field, computed_field

from typing import Annotated, List

from lecture_2.hw.shop_api.models import Cart as CartModel
from lecture_2.hw.shop_api.schemas.base import Base

__all__ = ["CartItem", "Cart"]


class CartItem(Base):
    """
    Represents pydantic base CartItem object.
    """

    id: int = Field(examples=[1])
    name: str = Field(examples=["Молоко"])
    quantity: int = Field(examples=[3])
    available: bool = Field(examples=[True])


class Cart(Base):
    """
    Represents pydantic base Cart object.
    """

    id: int = Field(examples=[1])
    items: Annotated[
        List[CartItem], Field(default=None, examples=[CartItem(id=1, name="Молоко", quantity=1, available=True)])
    ] = None
    price: Annotated[float, Field(default=0, examples=[234.4])] = 0

    @computed_field
    @property
    def quantity(self) -> int:
        return sum(item.quantity for item in self.items)

    @staticmethod
    def from_cart_model(cart: CartModel) -> Cart:
        """
        Creates Cart objects using provided SQLAlchemy data.
        """
        items: List[CartItem] = []
        for cart_item in cart.items:
            items.append(
                CartItem(
                    id=cart_item.item.id,
                    name=cart_item.item.name,
                    quantity=cart_item.quantity,
                    available=(not cart_item.item.deleted),
                )
            )

        return Cart(
            id=cart.id,
            items=items,
            price=cart.price,
        )
