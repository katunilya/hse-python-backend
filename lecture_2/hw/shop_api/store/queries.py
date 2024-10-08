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
    # Проверяем, есть ли уже товар в корзине
    for cart_item in cart["items"]:
        if cart_item["id"] == item_id:
            cart_item["quantity"] += 1
            cart["price"] += item["price"]
            return cart
    # Если товара нет, добавляем новый с quantity = 1
    cart["items"].append({"id": item_id, "quantity": 1, "price": item["price"]})
    cart["price"] += item["price"]
    return cart

def create_item(item_data: dict):
    global _item_id_counter
    _item_id_counter += 1
    item = {"id": _item_id_counter, "name": item_data["name"], "price": item_data["price"], "deleted": False}
    _data_items[_item_id_counter] = item
    return item

def get_item(item_id: int):
    item = _data_items.get(item_id)
    if item and not item["deleted"]:
        return item
    return None

def delete_item(item_id: int):
    item = _data_items.get(item_id)
    if not item:
        return False
    item["deleted"] = True
    return True