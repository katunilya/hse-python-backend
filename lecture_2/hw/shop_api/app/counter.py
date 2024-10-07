
class CounterService:
    def __init__(self):
        self.item_id_counter = 0
        self.cart_id_counter = 0

    def get_next_item_id(self) -> int:
        self.item_id_counter += 1
        return self.item_id_counter

    def get_next_cart_id(self) -> int:
        self.cart_id_counter += 1
        return self.cart_id_counter
