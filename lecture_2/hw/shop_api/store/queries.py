from typing import List, Optional
from lecture_2.hw.shop_api.store.models import Cart, CartItem, Item
from lecture_2.hw.shop_api.api.item.contracts import ItemRequest

_cart_data = {}
_item_data = {}
_cart_id_counter = 0
_item_id_counter = 0

def create_cart() -> Cart:
    global _cart_id_counter
    _cart_id_counter += 1
    cart = Cart(id=_cart_id_counter)
    _cart_data[_cart_id_counter] = cart
    return cart

def get_cart(cart_id: int) -> Optional[Cart]:
    return _cart_data.get(cart_id)

def get_carts(offset: int, limit: int, min_price: Optional[float], max_price: Optional[float]) -> List[Cart]:
    carts = list(_cart_data.values())
    if min_price is not None:
        carts = [cart for cart in carts if cart.price >= min_price]
    if max_price is not None:
        carts = [cart for cart in carts if cart.price <= max_price]
    return carts[offset:offset + limit]

def add_item_to_cart(cart_id: int, item_id: int) -> Optional[Cart]:
    cart = _cart_data.get(cart_id)
    item = _item_data.get(item_id)
    if not cart or not item:
        return None
    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            cart.price += item.price
            return cart
    cart.items.append(CartItem(id=item_id, name=item.name, quantity=1, available=True))
    cart.price += item.price
    return cart

def create_item(item_request: ItemRequest) -> Item:
    global _item_id_counter
    _item_id_counter += 1
    item = Item(id=_item_id_counter, name=item_request.name, price=item_request.price)
    _item_data[_item_id_counter] = item
    return item

def get_item(item_id: int) -> Optional[Item]:
    return _item_data.get(item_id)

def update_item(item_id: int, item_data: ItemRequest) -> Optional[Item]:
    item = _item_data.get(item_id)
    if not item or item.deleted:
        return None
    item.name = item_data.name
    item.price = item_data.price
    return item

def patch_item(item_id: int, item_data: ItemRequest) -> Optional[Item]:
    item = _item_data.get(item_id)
    if not item or item.deleted:
        return None
    if item_data.name is not None:
        item.name = item_data.name
    if item_data.price is not None:
        item.price = item_data.price
    return item

def delete_item(item_id: int) -> Optional[Item]:
    item = _item_data.get(item_id)
    if (not item) or item.deleted:
        return None
    item.deleted = True
    return item