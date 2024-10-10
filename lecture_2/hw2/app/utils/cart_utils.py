from app.models import Cart
from app.db import items_db, carts_db

   def recalculate_cart_price(cart: Cart):
       total_price = 0.0
       for cart_item in cart.items:
           item_in_db = items_db.get(cart_item.id)
           if item_in_db and not item_in_db.deleted:
               cart_item.available = True
               cart_item.name = item_in_db.name
               total_price += item_in_db.price * cart_item.quantity
           else:
               cart_item.available = False
       cart.price = total_price

   def update_carts_item_change(item_id: int):
       for cart in carts_db.values():
           cart_modified = False
           for cart_item in cart.items:
               if cart_item.id == item_id:
                   cart_modified = True
                   item_in_db = items_db[item_id]
                   cart_item.name = item_in_db.name
           if cart_modified:
               recalculate_cart_price(cart)

   def update_carts_item_deletion(item_id: int):
       for cart in carts_db.values():
           cart_modified = False
           for cart_item in cart.items:
               if cart_item.id == item_id:
                   cart_item.available = False
                   cart_modified = True
           if cart_modified:
               recalculate_cart_price(cart)