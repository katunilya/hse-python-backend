# models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from shop_api.database.database import Base

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    deleted = Column(Boolean, default=False)

class CartItem(Base):
    __tablename__ = 'cart_items'

    cart_id = Column(Integer, ForeignKey('carts.id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('items.id'), primary_key=True)
    quantity = Column(Integer, default=1)

    item = relationship('Item')

class Cart(Base):
    __tablename__ = 'carts'

    id = Column(Integer, primary_key=True, index=True)
    price = Column(Float)
    items = relationship('CartItem', backref='cart', cascade='all, delete-orphan')
