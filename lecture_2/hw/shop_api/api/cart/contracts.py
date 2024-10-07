from pydantic import BaseModel

class CartRequest(BaseModel):
    pass  # Тут можно добавить поля по необходимости

class CartResponse(BaseModel):
    id: int
    items: list
    price: float

    @staticmethod
    def from_entity(entity):
        return CartResponse(
            id=entity["id"],
            items=entity["items"],
            price=entity["price"]
        )