from typing import Dict
from .schemas import Item, Cart

last_item_id = 0
last_cart_id = 0


items_db: Dict[int, Item] = {}
carts_db: Dict[int, Cart] = {}
