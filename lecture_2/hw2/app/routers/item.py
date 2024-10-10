from fastapi import APIRouter, HTTPException, Path, Query
from typing import List, Optional
from app.models import Item, ItemCreate, ItemUpdate
from app.db import items_db, item_id_counter, db_lock
from app.utils.cart_utils import update_carts_item_change, update_carts_item_deletion

   router = APIRouter()

   @router.post("/item", response_model=Item)
   def create_item(item: ItemCreate):
       global item_id_counter
       with db_lock:
           item_id = item_id_counter
           item_id_counter += 1
           new_item = Item(id=item_id, name=item.name, price=item.price)
           items_db[item_id] = new_item
       return new_item

   @router.get("/item/{item_id}", response_model=Item)
   def get_item(item_id: int = Path(..., ge=1)):
       item = items_db.get(item_id)
       if not item or item.deleted:
           raise HTTPException(status_code=404, detail="Item not found")
       return item

   @router.get("/item", response_model=List[Item])
   def list_items(
       offset: int = Query(0, ge=0),
       limit: int = Query(10, gt=0),
       min_price: Optional[float] = Query(None, ge=0.0),
       max_price: Optional[float] = Query(None, ge=0.0),
       show_deleted: bool = Query(False)
   ):
       items = list(items_db.values())
       if not show_deleted:
           items = [item for item in items if not item.deleted]
       if min_price is not None:
           items = [item for item in items if item.price >= min_price]
       if max_price is not None:
           items = [item for item in items if item.price <= max_price]
       return items[offset:offset+limit]

   @router.put("/item/{item_id}", response_model=Item)
   def replace_item(item_id: int, item: ItemCreate):
       existing_item = items_db.get(item_id)
       if not existing_item:
           raise HTTPException(status_code=404, detail="Item not found")
       updated_item = Item(id=item_id, name=item.name, price=item.price, deleted=existing_item.deleted)
       items_db[item_id] = updated_item
       # Обновляем корзины
       update_carts_item_change(item_id)
       return updated_item

   @router.patch("/item/{item_id}", response_model=Item)
   def update_item(item_id: int, item_update: ItemUpdate):
       existing_item = items_db.get(item_id)
       if not existing_item:
           raise HTTPException(status_code=404, detail="Item not found")
       if item_update.name is not None:
           existing_item.name = item_update.name
       if item_update.price is not None:
           existing_item.price = item_update.price
       items_db[item_id] = existing_item
       # Обновляем корзины
       update_carts_item_change(item_id)
       return existing_item

   @router.delete("/item/{item_id}")
   def delete_item(item_id: int):
       existing_item = items_db.get(item_id)
       if not existing_item:
           raise HTTPException(status_code=404, detail="Item not found")
       existing_item.deleted = True
       items_db[item_id] = existing_item
       # Обновляем корзины
       update_carts_item_deletion(item_id)
       return {"detail": "Item marked as deleted"}