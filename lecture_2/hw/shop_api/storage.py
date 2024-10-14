from lecture_2.hw.shop_api.src.items.schema import Item
from lecture_2.hw.shop_api.src.carts.schema import Cart
from typing import Dict

carts: Dict[int, Cart] = {}
items: Dict[int, Item] = {}