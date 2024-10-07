from pydantic import BaseModel

class ItemRequest(BaseModel):
    name: str
    price: float

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool

    @staticmethod
    def from_entity(entity):
        return ItemResponse(
            id=entity["id"],
            name=entity["name"],
            price=entity["price"],
            deleted=entity["deleted"]
        )