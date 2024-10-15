from typing import List, Optional, Iterable

from lecture_2.hw.shop_api.api.store.models import (
    CartItem,
    Cart,
    Item
)

from lecture_2.hw.shop_api.api.item.contracts import (
    ItemRequest, 
    ItemPatchRequest
)

# генератор id для корзин
def int_cart_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1

# генератор id для товаров
def int_item_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1

_id_cart_generator = int_cart_id_generator()
_id_item_generator = int_item_id_generator()
_cart_data = dict[int, Cart]()
_item_data = dict[int, Item]()

# добавление новой корзины
def add_cart() -> Cart:
    _id = next(_id_cart_generator)
    new_cart = Cart(id=_id)
    _cart_data[_id] = new_cart
    return new_cart

# получение корзины по id
def get_cart(cart_id: int) -> Optional[Cart]:
    return _cart_data.get(cart_id)

# получение списка корзин с query-параметрами
def get_carts(
        min_price: Optional[float],
        max_price: Optional[float],
        min_quantity: Optional[int],
        max_quantity: Optional[int],
        offset: int = 0,
        limit: int = 10
) -> List[Cart]:
    carts = list(_cart_data.values())

    if min_price is not None:
       carts = [cart for cart in carts if cart.price >= min_price]
    if max_price is not None:
       carts = [cart for cart in carts if cart.price <= max_price]
    
    if min_quantity is not None:
        carts = [cart for cart in carts if sum(item.quantity for item in cart.items) >= min_quantity]
    if max_quantity is not None:
        carts = [cart for cart in carts if sum(item.quantity for item in cart.items) <= max_quantity]
   
    return carts[offset: offset + limit] 

# добавление предмета в корзину
def add_item_to_cart(cart_id: int, item_id: int) -> Optional[Cart]:
    cart = _cart_data.get(cart_id)
    item = _item_data.get(item_id)

    if not cart or not item:
        return None
    
    # если товар уже есть в корзине, увеличиваем его количество
    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            cart.price += item.price
            return cart

    # иначе добавляем новый товар в корзину    
    cart.items.append(CartItem(
        id=item_id,
        name=item.name,
        quantity=1,
        available=True
    ))
    cart.price += item.price
    return cart

# добавление нового предмета
def add_item(item_request: ItemRequest) -> Item:
    _id = next(_id_item_generator)
    new_item = Item(id=_id, name=item_request.name, price=item_request.price)
    _item_data[_id] = new_item
    return new_item

# получение товара по id
def get_item(item_id: int) -> Optional[Item]:
    return _item_data.get(item_id)

# получение списка товаров с query-параметрами
def get_items(
        min_price: Optional[float],
        max_price: Optional[float],
        offset: int = 0,
        limit: int = 10,
        show_deleted: bool = False
) -> List[Item]:
    items = list(_item_data.values())

    if min_price is not None:
       items = [item for item in items if item.price >= min_price]
    if max_price is not None:
       items = [item for item in items if item.price <= max_price]
    
    if not show_deleted:
        items = [item for item in items if not item.deleted]
   
    return items[offset: offset + limit]     

# замена товара по id
def replace_item(item_id: int, item_data: ItemRequest) -> Optional[Item]:
    item = _item_data.get(item_id)
    if not item:
        return None
    item.name = item_data.name
    item.price = item_data.price
    item.deleted = False
    return item

# частичное обновление товара по id
def patch_item(item_id: int, item_data: ItemRequest) -> Optional[Item]:
    item = _item_data.get(item_id)
    if not item:
        return None
    if item_data.name is not None:
        item.name = item_data.name
    if item_data.price is not None:
        item.price = item_data.price
    return item

# удаление товара по id
def delete_item(item_id: int) -> Optional[Item]:
    item = _item_data.get(item_id)
    if item is None:
        return None
    item.deleted = True
    return item