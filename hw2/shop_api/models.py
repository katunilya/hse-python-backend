from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    deleted = Column(Boolean, default=False)


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    price = Column(Float, default=0.0)
    items = relationship("CartItem", back_populates="cart")


class CartItem(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey('carts.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)

    cart = relationship("Cart", back_populates="items")
    item = relationship("Item")
