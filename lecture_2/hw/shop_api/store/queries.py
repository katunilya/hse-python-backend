from typing import List, Optional

# Храним данные корзин и товаров
_data_carts = dict[int, dict]()
_data_items = dict[int, dict]()
_cart_id_counter = 0
_item_id_counter = 0

# Создаём корзину с начальной ценой 0 и пустым списком товаров
def create_cart() -> dict:
    global _cart_id_counter
    _cart_id_counter += 1
    cart = {"id": _cart_id_counter, "items": [], "price": 0.0}
    _data_carts[_cart_id_counter] = cart
    return cart

# Получаем корзину по её ID, если она существует
def get_cart(cart_id: int) -> Optional[dict]:
    cart = _data_carts.get(cart_id)
    if not cart:
        return None

    # Если корзина пуста, возвращаем её с нулевой ценой и пустыми товарами
    if not cart["items"]:
        return {
            "id": cart["id"],
            "items": [],
            "price": 0.0
        }

    # Пересчитываем итоговую цену для корзины
    total_price = 0
    valid_items = []
    for item in cart["items"]:
        valid_item = get_item(item["id"])  # Получаем информацию о товаре по ID
        if valid_item:
            item_total_price = valid_item["price"] * item["quantity"]  # Цена товара с учётом количества
            total_price += item_total_price
            valid_items.append({
                "id": valid_item["id"],
                "name": valid_item["name"],
                "price": valid_item["price"],
                "quantity": item["quantity"]
            })

    return {
        "id": cart["id"],
        "items": valid_items,  # Список товаров в корзине
        "price": total_price   # Итоговая цена корзины
    }

# Добавляем товар в корзину, увеличиваем количество, если товар уже есть
def add_item(cart_id: int, item_id: int) -> Optional[dict]:
    cart = _data_carts.get(cart_id)
    item = _data_items.get(item_id)
    if not cart or not item:
        return None

    # Проверяем, есть ли уже товар в корзине
    for cart_item in cart["items"]:
        if cart_item["id"] == item_id:
            cart_item["quantity"] += 1  # Увеличиваем количество, если товар уже есть
            cart["price"] += item["price"]  # Увеличиваем цену корзины
            return cart

    # Если товара нет, добавляем новый с количеством 1
    cart["items"].append({
        "id": item_id,
        "quantity": 1,  # Новый товар с количеством 1
        "price": item["price"]
    })
    cart["price"] += item["price"]  # Увеличиваем цену корзины
    return cart

# Создаём новый товар
def create_item(item_data: dict) -> dict:
    global _item_id_counter
    _item_id_counter += 1
    item = {"id": _item_id_counter, "name": item_data["name"], "price": item_data["price"], "deleted": False}
    _data_items[_item_id_counter] = item
    return item

# Получаем товар по его ID, если он не удалён
def get_item(item_id: int) -> Optional[dict]:
    item = _data_items.get(item_id)
    if item and not item["deleted"]:
        return item
    return None

# Удаляем товар
def delete_item(item_id: int) -> bool:
    item = _data_items.get(item_id)
    if not item:
        return False
    item["deleted"] = True
    return True

# Получаем список корзин с возможностью фильтрации по цене и количеству
def get_carts(offset: int, limit: int, min_price: Optional[float], max_price: Optional[float],
              min_quantity: Optional[int], max_quantity: Optional[int]) -> List[dict]:
    carts = list(_data_carts.values())

    # Фильтруем корзины по цене
    if min_price is not None:
        carts = [cart for cart in carts if cart["price"] >= min_price]
    if max_price is not None:
        carts = [cart for cart in carts if cart["price"] <= max_price]

    # Фильтруем по количеству товаров
    if min_quantity is not None:
        carts = [cart for cart in carts if sum(item["quantity"] for item in cart["items"]) >= min_quantity]
    if max_quantity is not None:
        carts = [cart for cart in carts if sum(item["quantity"] for item in cart["items"]) <= max_quantity]

    # Пагинация
    return carts[offset:offset + limit]