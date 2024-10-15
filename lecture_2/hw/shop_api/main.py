from fastapi import FastAPI, HTTPException, Query, Response
from http import HTTPStatus
from typing import Optional
from .model import Cart, CartItem, Item, ItemPost
from typing import Iterable

app = FastAPI(title="Shop API")

carts_db = {}
items_db = {}

def cart_id_generator() -> Iterable[int]:
    cart_id = 0
    while True:
        yield cart_id
        cart_id += 1

def item_id_generator() -> Iterable[int]:
    item_id = 0
    while True:
        yield item_id
        item_id += 1

cart_id = cart_id_generator()
item_id = item_id_generator()

@app.post("/cart", status_code=201)
async def create_cart(response: Response):
    id = next(cart_id)
    if id in carts_db:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, 
                            detail="Cart with this id already exist")
    cart = Cart(id=id, items=[], price=0.0, total_quantity=0)
    carts_db[id] = cart
    response.headers["location"] = f"/cart/{id}"
    return cart

@app.get("/cart/{id}", status_code=200)
async def get_cart(id: int):
    if id not in carts_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, 
                            detail=f"Can't find cart with id - {id}")
    return carts_db[id]

@app.get("/cart", status_code=200)
async def carts_list(offset: int = Query(0, ge=0), 
                     limit: int = Query(10, ge=1), 
                     min_price: Optional[float] = Query(None, ge=0.0), 
                     max_price: Optional[float] = Query(None, ge=0.0), 
                     min_quantity: Optional[int] = Query(None, ge=0), 
                     max_quantity: Optional[int] = Query(None, ge=0)):
    carts_db_values = [val for _, val in carts_db.items()]
    if min_price is None:
        min_price = 0.0
    if max_price is None:
        max_price = float('inf')
    if min_quantity is None:
        min_quantity = 0
    if max_quantity is None:
        max_quantity = float('inf')
    correct_carts = []
    for cart in carts_db_values:
        cart_items_total_quantity = sum(item.quantity for item in cart.items)
        if cart.price >= min_price and cart.price <= max_price and cart_items_total_quantity >= min_quantity and cart_items_total_quantity <= max_quantity:
            correct_carts.append(cart)
    return correct_carts[offset:offset + limit]

@app.post("/cart/{cart_id}/add/{item_id}", status_code=201)
async def add_item_to_cart(cart_id: int, item_id: int):
    if cart_id not in carts_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, 
                            detail=f"Can't find {cart_id} in carts db")
    if item_id not in items_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, 
                            detail=f"Can't find {item_id} in items db")
    visited = False
    for item in carts_db[cart_id].items:
        if item.id == item_id:
            item.quantity += 1
            visited = True
    if not visited:
        item = items_db[item_id]
        carts_db[cart_id].items.append(CartItem(id=item_id, name=item.name, quantity=1, available=not item.deleted))
    carts_db[cart_id].total_quantity += 1
    carts_db[cart_id].price += items_db[item_id].price
    return item

@app.post("/item", status_code=201)
async def add_item(item: ItemPost):
    id = next(item_id)
    item = Item(id=id, name=item.name, price=item.price)
    items_db[id] = item
    return item

@app.get("/item/{id}", status_code=200)
async def get_item_by_id(id: int):
    if id not in items_db or items_db[id].deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, 
                            detail=f"Id {id} doesn't exist in items db")
    item = items_db[id]
    return item

@app.get("/item", status_code=200)
async def carts_list(offset: int = Query(0, ge=0), 
                     limit: int = Query(10, ge=1), 
                     min_price: Optional[float] = Query(None, ge=0.0), 
                     max_price: Optional[float] = Query(None, ge=0.0), 
                     show_deleted: bool = False):
    items_db_values = [val for _, val in items_db.items()]
    if min_price is None:
        min_price = 0.0
    if max_price is None:
        max_price = float('inf')
    correct_items = []
    for item in items_db_values:
        if not show_deleted and item.deleted:
            continue
        if item.price >= min_price and item.price <= max_price:
            correct_items.append(item)
    return correct_items[offset:offset + limit]

@app.put("/item/{id}", status_code=200)
async def change_item_by_id(id: int, item: ItemPost):
    if id not in items_db or not item.name or not item.price:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, 
                            detail=f"Can't change non existing item with id - {id}")
    elif items_db[id].deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, 
                            detail=f"Can't change deleted item - {items_db[id]}")
    existed_item = items_db[id]
    existed_item.name = item.name
    existed_item.price = item.price
    return existed_item

@app.patch("/item/{id}", status_code=200)
async def partial_change_item_by_id(id: int, item: ItemPost):
    if id not in items_db:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, 
                            detail=f"Can't change non existing item with id - {id}")
    elif items_db[id].deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, 
                            detail=f"Can't change deleted item - {items_db[id]}")
    existed_item = items_db[id]
    existed_item.name = item.name
    existed_item.price = item.price
    return existed_item

@app.delete("/item/{id}", status_code=200)
async def delete_item(id: int):
    if id not in items_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, 
                            detail=f"Can't delete non existing item with id - {id}")
    items_db[id].deleted = True
    return items_db[id]