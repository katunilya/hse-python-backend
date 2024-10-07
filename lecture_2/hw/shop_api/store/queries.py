_data_carts = {}
_data_items = {}
_cart_id_counter = 0
_item_id_counter = 0

def create_cart():
    global _cart_id_counter
    _cart_id_counter += 1
    cart = {"id": _cart_id_counter, "items": [], "price": 0.0}
    _data_carts[_cart_id_counter] = cart
    return cart

def get_cart(cart_id: int):
    return _data_carts.get(cart_id)

def add_item(cart_id: int, item_id: int):
    cart = _data_carts.get(cart_id)
    item = _data_items.get(item_id)
    if not cart or not item:
        return None
    cart["items"].append(item)
    cart["price"] += item["price"]
    return cart

def create_item(item_data: dict):
    global _item_id_counter
    _item_id_counter += 1
    item = {"id": _item_id_counter, "name": item_data["name"], "price": item_data["price"], "deleted": False}
    _data_items[_item_id_counter] = item
    return item

def get_item(item_id: int):
    return _data_items.get(item_id)

def delete_item(item_id: int):
    item = _data_items.get(item_id