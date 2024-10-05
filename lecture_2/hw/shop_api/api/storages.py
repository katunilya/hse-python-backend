from typing import Iterable
from lecture_2.hw.shop_api.api.cart.entities import CartInfo, ItemInCart
from lecture_2.hw.shop_api.api.item.entities import ItemInfo

def _int_cart_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1

def _int_item_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1

cart_id_generator = _int_cart_id_generator()
item_id_generator = _int_item_id_generator()

cart_data = dict[int, CartInfo]()
item_data = dict[int, ItemInfo]()
