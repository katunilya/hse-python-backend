from fastapi import APIRouter, HTTPException, Path, Query
from typing import List, Optional
from app.models import Cart, CartItem
from app.db import carts_db, cart_id_counter, db_lock, items_db
from app.utils.cart_utils import recalculate_cart_price

   router = APIRouter()

   @router.post("/cart")
   def create_cart():
       global cart_id_counter
       with db_lock:
           cart_id = cart_id_counter
           cart_id_counter += 1
           new_cart = Cart(id=cart_id)
           carts_db[cart_id] = new_cart
       return {"id": cart_id}

   @router.get("/cart/{cart_id}", response_model=Cart)
   def get_cart(cart_id: int):
       cart = carts_db.get(cart_id)
       if not cart:
           raise HTTPException(status_code=404, detail="Cart not found")
       return cart

   @router.get("/cart", response_model=List[Cart])
   def list_carts(
       offset: int = Query(0, ge=0),
       limit: int = Query(10, gt=0),
       min_price: Optional[float] = Query(None),
       max_price: Optional[float] = Query(None),
       min_quantity: Optional[int] = Query(None, ge=0),
       max_quantity: Optional[int] = Query(None, ge=0)
   ):
       carts = list(carts_db.values())
       if min_price is not None:
           carts = [cart for cart in carts if cart.price >= min_price]
       if max_price is not None:
           carts = [cart for cart in carts if cart.price <= max_price]
       if min_quantity is not None:
           carts = [cart for cart in carts if sum(item.quantity for item in cart.items) >= min_quantity]
       if max_quantity is not None:
           carts = [cart for cart in carts if sum(item.quantity for item in cart.items) <= max_quantity]
       return carts[offset:offset+limit]

   @router.post("/cart/{cart_id}/add/{item_id}")
   def add_item_to_cart(cart_id: int, item_id: int):
       cart = carts_db.get(cart_id)
       if not cart:
           raise HTTPException(status_code=404, detail="Cart not found")
       item = items_db.get(item_id)
       if not item or item.deleted:
                      raise HTTPException(status_code=404, detail="Item not found or deleted")

       for cart_item in cart.items:
           if cart_item.id == item_id:
               cart_item.quantity += 1
               break
       else:
           cart_item = CartItem(
               id=item_id,
               name=item.name,
               quantity=1,
               available=not item.deleted
           )
           cart.items.append(cart_item)

       recalculate_cart_price(cart)
       return {"detail": "Item added to cart"}