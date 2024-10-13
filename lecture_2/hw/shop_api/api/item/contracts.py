from pydantic import BaseModel


class ItemRequest(BaseModel):
    name: str = None
    price: float = None

    model_config = {
        "extra" : "forbid"
    }
