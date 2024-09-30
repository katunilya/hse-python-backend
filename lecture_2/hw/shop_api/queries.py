from typing import List, Optional

from .models import Cart, Item, ItemInCart
from .iterator import generate_id


_items: dict[int, Item] = []
_carts: dict[int, Cart] = []

def get_item(item_id: int) -> Item:
    for item in _items:
        if item.id == item_id and item.deleted is False:
            return item
    return None

def get_items(   
    offset: int,
    limit: int,
    min_price: float,
    max_price: float,
    show_deleted: bool
) -> List[Item]:
    if offset < 0:
        raise ValueError("Offset must be a non-negative integer.")
    
    if limit <= 0:
        raise ValueError("Limit must be a non-negative integer, except zero.")
    
    if offset >= len(_carts):
        return []
    
    if min_price or max_price is not None:
        if min_price or max_price  < 0:
            raise ValueError("Min and max values must be non-negative.")
    
    if offset >= len(_items):
        return []
    
    items_slice = _items[offset:offset + limit]
    
    filtered_items = [
        item for item in items_slice
        if (min_price is None or item.price >= min_price)
        and (max_price is None or item.price <= max_price)
        and (show_deleted or not item.deleted)
    ]
    
    return filtered_items

def change_item(item_id: int, new_item: Item) -> Item:
    item = get_item(item_id)
    if item:
        item.name = new_item.name
        item.price = new_item.price
        item.deleted = new_item.deleted
        return item
    else:
        raise ValueError(f"Item {item_id} not found.")

def add_item(item: Item) -> Item:
    item.id = generate_id()
    _items.append(item)
    return item

def modify_item(item_id: int, new_name: Optional[str] = None, new_price: Optional[float] = None) -> Item:
    item = get_item(item_id)
    if item:
        if new_name is not None:
            item.name = new_name
        if new_price is not None:
            item.price = new_price
        return item
    else:
        raise ValueError(f"Item {item_id} not found.")

def delete_item(item_id: int) -> Item:
    item = get_item(item_id)
    if item:
        item.deleted = True

        
def get_cart(cart_id: int) -> Cart:
    for cart in _carts:
        if cart.id == cart_id:
            return cart

def get_carts(
    offset: int,
    limit: int,
    min_price: float,
    max_price: float,
    min_quantity: int,
    max_quantity: int
) -> List[Cart]:
    if offset < 0:
        raise ValueError("Offset must be a non-negative integer.")
    
    if limit <= 0:
        raise ValueError("Limit must be a non-negative integer, except zero.")
    
    if offset >= len(_carts):
        return []
    
    if min_price or max_price or min_quantity or max_quantity is not None:
        if any(value is not None and value < 0 for value in [min_price, max_price, min_quantity, max_quantity]):
            raise ValueError("Min and max values must be non-negative.")
    
    carts_slice = _carts[offset:offset + limit]
    
    filtered_carts = [
        cart for cart in carts_slice
        if (min_price is None or cart.price >= min_price)
        and (max_price is None or cart.price <= max_price)
        and (min_quantity is None or sum(item.quantity for item in cart.items) >= min_quantity)
        and (max_quantity is None or sum(item.quantity for item in cart.items) <= max_quantity)
    ]
    
    return filtered_carts

def add_item_in_cart(cart_id: int, item_id: int) -> Cart:
    cart = get_cart(cart_id)
    new_item = get_item(item_id)
    if cart is None:
        raise ValueError(f"Cart with id {cart_id} not found.")
    if new_item is None:
        raise ValueError(f"Item with id {item_id} not found.")
    for item in cart.items:
        if item.id == item_id and item.available == True:
            item.quantity += 1
            cart.price += new_item.price
            return cart
    cart.items.append(ItemInCart(id=new_item.id, name=new_item.name, quantity=1, available=True))
    cart.price += new_item.price
    return cart

def create_cart() -> Cart:
    cart_id = generate_id()
    _carts.append(Cart(id=cart_id))
    return Cart(id=cart_id)