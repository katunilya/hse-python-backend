from sqlalchemy import Boolean, Column, Float, Integer, String

from lecture_2.hw.shop_api.storage.db import Base

__all__ = ["Item"]


class Item(Base):
    """
    Represents items SQL table
    """

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)
