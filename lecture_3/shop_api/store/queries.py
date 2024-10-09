from typing import Iterable
from .models import *

data_carts = dict[int, Cart]()
data_items = dict[int, Item]()

def int_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1

cart_id_generator = int_id_generator()
item_id_generator = int_id_generator()

