from pydantic import BaseModel

# Модель запроса для создания или обновления товара
class ItemRequest(BaseModel):
    name: str
    price: float

# Модель ответа для отображения данных о товаре
class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False  # По умолчанию товар не удалён

    @staticmethod
    def from_entity(entity):
        return ItemResponse(
            id=entity["id"],
            name=entity["name"],
            price=entity["price"],
            deleted=entity.get("deleted", False)  # По умолчанию считаем, что товар не удалён
        )