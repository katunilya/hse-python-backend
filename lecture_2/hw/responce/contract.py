from pydantic import BaseModel
from lecture_2.hw.models.item import *
from lecture_2.hw.models.cart import *

class ItemResponce(BaseModel):
    id: int
    price: float
    name: str
    deleted: bool

    @staticmethod
    def from_item(item: Item) -> "ItemResponce":
        return ItemResponce(
            id=item.id,
            name=item.item.name,
            deleted=item.item.deleted,
            price=item.item.price,
        )
        
class CartResponce(BaseModel):
    id: int
    price: float
    items: List[ItemInCart]
    @staticmethod
    def from_cart(cart: Cart) -> "CartResponce":
        return CartResponce(
            id=cart.id,
            price=cart.price,
            items=[ItemInCart(
                id=item.id,
                name=item.name,
                deleted=item.deleted,
                quantity=item.quantity 
            ) for item in cart.items]
        )


class ItemRequest(BaseModel):
    name: str
    price: float

    def as_item(self) -> InitItem:
        return InitItem(name=self.name, price=self.price)
    
class CartRequest(BaseModel):
    id: int
    def as_cart(self) -> Cart:
        return Cart(id=id)


class PatchItemRequest(BaseModel):
    name: str | None = None
    price: float | None = None

    model_config = ConfigDict(extra="forbid")

    def as_patch_item(self) -> ItemPatch:
        return ItemPatch(name=self.name, price=self.price)
    

    
