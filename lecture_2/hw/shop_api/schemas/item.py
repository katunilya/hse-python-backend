from pydantic import Field

from typing import Annotated, Optional

from lecture_2.hw.shop_api.schemas.base import Base

__all__ = ["Item", "ItemCreate", "ItemReplace", "ItemUpdate"]


class Item(Base):
    """
    Represents pydantic base Item object.
    """

    id: int = Field(examples=[1])
    name: str = Field(examples=["Молоко"])
    price: float = Field(examples=[159.99])
    deleted: bool = Field(default=False, examples=[True])


class ItemCreate(Base):
    """
    Represents pydantic ItemCreate object for create request.
    """

    name: str = Field(examples=["Молоко"])
    price: float = Field(examples=[159.99])


class ItemReplace(Base):
    """
    Represents pydantic ItemCreate object for replace request.
    """

    name: str = Field(examples=["Молоко"])
    price: float = Field(examples=[159.99])
    deleted: bool = Field(default=False, examples=[True])


class ItemUpdate(Base):
    """
    Represents pydantic ItemCreate object for update request.
    """

    name: Annotated[Optional[str], Field(examples=["Молоко"])] = None
    price: Annotated[Optional[float], Field(examples=[159.99])] = None
