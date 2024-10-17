from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, Column, Integer, ForeignKey, String, Float, Boolean, Table
from typing_extensions import Any

#SQLALCHEMY_DATABASE_URL = "sqlite:///./shop.db"



@as_declarative()
class Base:
    metadata = None
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

connect_table = Table('cart_item_association', Base.metadata,
                          Column('cart_id', Integer, ForeignKey('cart.id')),
                          Column('item_id', Integer, ForeignKey('item.id')),
                          Column('quantity', Integer, default=1)
                          )

class CartTable(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, index=True)
    items = relationship("ItemTable", secondary=connect_table, back_populates="cart")
    available = Column(Boolean, default=True)
    price = Column(Float, default=0.0)

class ItemTable(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    deleted = Column(Boolean, default=False)
    cart_id = Column(Integer, ForeignKey("cart.id"))
    cart = relationship("CartTable", secondary=connect_table, back_populates="items")
    quantity = Column(Integer, default=0)    