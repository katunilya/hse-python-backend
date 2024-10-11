from typing import Dict
from models import Item, Cart


class DataStore:
    def __init__(self):
        self.items_db: Dict[int, Item] = {}
        self.carts_db: Dict[int, Cart] = {}
        self.item_id_counter: int = 0
        self.cart_id_counter: int = 0

    def get_new_item_id(self) -> int:
        self.item_id_counter += 1
        return self.item_id_counter

    def get_new_cart_id(self) -> int:
        self.cart_id_counter += 1
        return self.cart_id_counter


data_store = DataStore()
