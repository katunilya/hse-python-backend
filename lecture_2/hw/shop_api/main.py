from fastapi import FastAPI, HTTPException, Response, status, Query
from .models import Item, Cart, CartItem
from typing import List, Optional, Annotated
from pydantic import NonNegativeInt, PositiveInt, NonNegativeFloat

app = FastAPI(title="Shop API")

items_db = {}
carts_db = {}
next_item_id = 1
next_cart_id = 1

@app.post('/item')
def create_item(item: Item, response: Response):
    global next_item_id
    item.id = next_item_id
    items_db[next_item_id] = item
    next_item_id += 1
    response.status_code = status.HTTP_201_CREATED
    response.headers["Location"] = f'/item/{item.id}'
    return item

@app.get("/item/{id}")
def get_item(id: int):
    item = items_db.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=404,
                            detail="Item not found")
    return item

@app.get("/item")
def list_items(offset: Annotated[NonNegativeInt, Query()] = 0,
               limit: Annotated[PositiveInt, Query()] = 10,
               min_price: Annotated[NonNegativeFloat, Query()] = None,
               max_price: Annotated[NonNegativeFloat, Query()] = None,
               show_deleted: bool = False):
    items = list(items_db.values())[offset:offset+limit]
    if min_price is not None:
        items = [item for item in items if item.price >= min_price]
    if max_price is not None:
        items = [item for item in items if item.price <= max_price]
    if not show_deleted:
        items = [item for item in items if not item.deleted]
    return items

@app.put("/item/{id}")
def update_item(id: int, item: Item):
    item_to_edit = items_db.get(id)
    if not item_to_edit or item_to_edit.deleted:
        raise HTTPException(status_code=404,
                            detail="Item not found")
    item.id = id
    items_db[id] = item
    return item

@app.patch("/item/{id}")
def patch_item(id: int, item: dict):
    item_to_patch = items_db.get(id)
    if not item_to_patch or item_to_patch.deleted:
        raise HTTPException(status_code=304,
                            detail="Item not modified")
    
    for key, value in item.items():
        if key == "deleted" and value:
            raise HTTPException(status_code=422,
                                detail="Cannot delete item")
        if not hasattr(item_to_patch, key):
            raise HTTPException(status_code=422,
                                detail=f"Attribute '{key}' not found")
        setattr(item_to_patch, key, value)
    
    return item_to_patch

@app.delete("/item/{id}")
def delete_item(id: int):
    if id not in items_db:
        raise HTTPException(status_code=404,
                            detail="Item not found")
    item = items_db[id]
    item.deleted = True
    return item

@app.post("/cart")
def create_cart(response: Response):
    global next_cart_id
    cart = Cart(id=next_cart_id, items=[], price=0)
    carts_db[next_cart_id] = cart
    next_cart_id += 1
    response.status_code = status.HTTP_201_CREATED
    response.headers["Location"] = f'/cart/{cart.id}'
    return {"id": cart.id}

@app.get("/cart/{id}")
def get_cart(id: int):
    cart = carts_db.get(id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@app.get("/cart")
def list_carts(offset: Annotated[NonNegativeInt, Query()] = 0,
               limit: Annotated[PositiveInt, Query()] = 10,
               min_price: Annotated[NonNegativeFloat, Query()] = None,
               max_price: Annotated[NonNegativeFloat, Query()] = None,
               min_quantity: Annotated[NonNegativeInt, Query()] = None,
               max_quantity: Annotated[NonNegativeInt, Query()] = None):
    carts = list(carts_db.values())[offset:offset+limit]
    if min_price is not None:
        carts = [cart for cart in carts if cart.price >= min_price]
    if max_price is not None:
        carts = [cart for cart in carts if cart.price <= max_price]
    if min_quantity is not None:
        carts = [cart for cart in carts if sum(item.quantity for item in cart.items) >= min_quantity]
    if max_quantity is not None:
        carts = [cart for cart in carts if sum(item.quantity for item in cart.items) <= max_quantity]
    return carts

@app.post('/cart/{cart_id}/add/{item_id}')
def add_item_to_cart(cart_id: int, item_id: int):
    if cart_id not in carts_db:
        raise HTTPException(status_code=404,
                            detail="Cart not found")
    if item_id not in items_db or items_db[item_id].deleted:
        raise HTTPException(status_code=404,
                            detail="Item not found or deleted")
    
    cart = carts_db[cart_id]
    item = items_db[item_id]
    
    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            break
    else:
        cart.items.append(CartItem(id=item.id,
                                   name=item.name,
                                   quantity=1,
                                   available=True))
    cart.price += item.price
    return {"status": "Item added"}

@app.delete('/cart/{cart_id}/remove/{item_id}')
def remove_item_from_cart(cart_id: int, item_id: int):
    if cart_id not in carts_db:
        raise HTTPException(status_code=404,
                            detail="Cart not found")
    
    cart = carts_db[cart_id]
    for cart_item in cart.items:
        if cart_item.id == item_id:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                cart.items.remove(cart_item)
            cart.price -= items_db[item_id].price
            return {"status": "Item removed"}
    
    raise HTTPException(status_code=404,
                        detail="Item not found in cart")

@app.delete('/cart/{cart_id}')
def delete_cart(cart_id: int):
    if cart_id not in carts_db:
        raise HTTPException(status_code=404,
                            detail="Cart not found")
    del carts_db[cart_id]
    return {"status": "Cart deleted"}