from lecture_2.hw.models.item import *
from lecture_2.hw.models.cart import *
from typing import Any, Callable, Dict, Iterable, TypeVar, Union


def int_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1

id_generator = int_id_generator()
items = dict[int, Item]()
carts = dict[int, Cart]()

def add(store: Dict[int, Union[Cart, Item]], item: Optional[InitItem] = None) -> Union[Cart, Item]:
    _id = next(id_generator) 
    if isinstance(item, InitItem):
        store[_id] = Item(id=_id, item=item) 
    else:
        store[_id] = Cart(id=_id, price=0.0, items=[])
    return store[_id]

    
def get(id: int, flag: bool) -> Union[Cart, Item, None]: #flag : 1 - cart, 0 - item, None, если элемент не найдется
    return items.get(id) if flag == 0 else carts.get(id)

def delete_item(id: int) -> bool: #только item
    items[id].item.deleted = True
    return False

def replace_item(id: int, updated_item: Item) -> Union[None, Item]:
    if id not in items:
        return None
    existing_item = items[id]
    existing_item.item.name = updated_item.name
    existing_item.item.price = updated_item.price
    existing_item.item.deleted = updated_item.deleted
    return existing_item

def patch_item(id: int, item: ItemPatch) -> Union[None, Item]:
    if id not in items or items.get(id).item.deleted:
        return None
    
    if item.name is not None:
        items[id].item.name = item.name

    if item.price is not None:
        items[id].item.price = item.price
    
    return items[id]

def add_item_to_cart(item_id: int, cart_id: int) -> Union[None, Cart]:
    global items
    if cart_id not in carts:
        return None
    if items[item_id].item.deleted:
        items[item_id].item.deleted = False
    cart = carts[cart_id]
    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1  
            cart.price += items[item_id].item.price
            return cart
    new_cart_item = ItemInCart(
        id=item_id,
        name=items[item_id].item.name,
        deleted=items[item_id].item.deleted,
        quantity=1  
    )
    cart.items.append(new_cart_item)
    cart.price += items[item_id].item.price
    return cart
   

T = TypeVar('T')

def filter_entities(
    entities: Dict[int, T],
    filter_func: Callable[[T], bool],
    offset: int = 0,
    limit: int = 10
) -> List[T]:
    filtered_entities = [entity for entity in entities.values() if filter_func(entity)]
    return filtered_entities[offset:offset + limit]

def filter_items(
    items: Dict[int, Item],
    offset: int = 0,
    limit: int = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    show_deleted: bool = False
) -> List[Item]:
    def item_filter(item: Item) -> bool:
        return (show_deleted or not item.item.deleted) and \
               (min_price is None or item.item.price >= min_price) and \
               (max_price is None or item.item.price <= max_price)

    return filter_entities(items, item_filter, offset, limit)

def filter_carts(
    carts: Dict[int, Cart],
    offset: int = 0,
    limit: int = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_quantity: Optional[int] = None,
    max_quantity: Optional[int] = None
) -> List[Cart]:
    def cart_filter(cart: Cart) -> bool:
        total_quantity = sum(item.quantity for item in cart.items)
        return (min_price is None or cart.price >= min_price) and \
               (max_price is None or cart.price <= max_price) and \
               (min_quantity is None or total_quantity >= min_quantity) and \
               (max_quantity is None or total_quantity <= max_quantity)
    
    return filter_entities(carts, cart_filter, offset, limit)


    