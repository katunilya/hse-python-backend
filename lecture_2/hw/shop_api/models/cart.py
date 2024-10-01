from sqlalchemy import Column, Float, ForeignKey, Integer, text
from sqlalchemy.orm import relationship

from lecture_2.hw.shop_api.storage.db import Base

__all__ = ["Cart", "CartItem"]


class Cart(Base):
    """
    Represents `carts` SQL table.
    """

    __tablename__ = "carts"

    id = Column(Integer, primary_key=True)
    items = relationship("CartItem")
    price = Column(Float, server_default=text("0"))
    quantity = Column(Integer, server_default=text("0"))


class CartItem(Base):
    """
    Represents `carts_items` SQL table.
    """

    __tablename__ = "carts_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    item = relationship("Item", foreign_keys=item_id)
    quantity = Column(Integer, nullable=False)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
