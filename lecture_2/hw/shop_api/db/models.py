from dataclasses import dataclass


def int_id_generator():
    i = 0
    while True:
        yield i
        i += 1


_id_cart_generator = int_id_generator()
_id_item_generator = int_id_generator()
_id_cart_item_generator = int_id_generator()


@dataclass(slots=True)
class CartItem:
    id: int = 0
    name: str = "CartItem"
    quantity: int = 0
    available: bool = True
    price: float = 0.0

    @staticmethod
    def createCartItem(idGen=_id_cart_item_generator):
        return CartItem(
            id=next(idGen),
            name="CartItem",
            quantity=0,
            available=True,
            price=0
        )

    def toResponse(self):
        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "available": self.available,
            "price": self.price,
        }


@dataclass(slots=True)
class Cart:
    id: int = 0
    items: list[CartItem] = None
    price: float = 0.0

    @staticmethod
    def createCart(idGen=_id_cart_generator):
        return Cart(
            id=next(idGen),
            items=[],
            price=0,
        )

    def toResponse(self):
        return {
            "id": self.id,
            "items": [item.toResponse() for item in self.items],
            "price": self.price
        }


@dataclass(slots=True)
class Item:
    id: int = 0
    name: str = "Item"
    price: float = 0.0
    deleted: bool = False

    @staticmethod
    def createItem(idGen=_id_item_generator):
        return Item(
            id=next(idGen),
            name="New Item",
            price=0,
            deleted=False
        )

    def toResponse(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "deleted": self.deleted
        }

    def toCartItem(self):
        return CartItem(
            id=self.id,
            name=self.name,
            quantity=1,
            available=True,
            price=self.price
        )
