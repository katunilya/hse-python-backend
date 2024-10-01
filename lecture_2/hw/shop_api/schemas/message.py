from pydantic import Field

from lecture_2.hw.shop_api.schemas.base import Base

__all__ = ["Message"]


class Message(Base):
    """
    Represents pydantic Message object.
    """

    message: str = Field(examples=["Message with information"])
