from pydantic import BaseModel

__all__ = ["Base"]


class Base(BaseModel):
    """
    Represents Base class for pydantic objects.
    """

    class Config:
        from_attributes = True
        extra = "forbid"
