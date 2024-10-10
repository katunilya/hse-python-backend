from threading import Lock

   items_db = {}
   carts_db = {}
   item_id_counter = 1
   cart_id_counter = 1
   db_lock = Lock()