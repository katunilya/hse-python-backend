from fastapi import FastAPI, HTTPException, Path, Query, Body, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import json

app = FastAPI()

class ItemCreate(BaseModel):
    name: str
    price: float = Field(..., gt=0.0)

    class Config:
        extra = 'forbid' 

class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False

class ItemUpdate(BaseModel):
    name: str
    price: float = Field(..., gt=0.0)

    class Config:
        extra = 'forbid'

class ItemPatch(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = Field(None, gt=0.0)

    class Config:
        extra = 'forbid'

class CartItem(BaseModel):
    id: int  # item id
    name: str
    quantity: int
    available: bool

class Cart(BaseModel):
    id: int
    items: List[CartItem] = []
    price: float = 0.0
    quantity: int = 0

items_db: Dict[int, Item] = {}
items_id_counter = 0

carts_db: Dict[int, Cart] = {}
carts_id_counter = 0

@app.post("/cart", status_code=201)
def create_cart():
    global carts_id_counter
    cart_id = carts_id_counter
    carts_id_counter += 1
    cart = Cart(id=cart_id)
    carts_db[cart_id] = cart
    response = {"id": cart_id}
    headers = {"Location": f"/cart/{cart_id}"}
    return JSONResponse(content=response, status_code=201, headers=headers)

@app.get("/cart/{id}", response_model=Cart)
def get_cart(id: int = Path(..., ge=0)):
    cart = carts_db.get(id)
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    total_price = 0.0
    total_quantity = 0
    for cart_item in cart.items:
        item = items_db.get(cart_item.id)
        if item is None:
            cart_item.available = False
        else:
            cart_item.available = not item.deleted
            cart_item.name = item.name
            if not item.deleted:
                total_price += item.price * cart_item.quantity
                total_quantity += cart_item.quantity
    cart.price = total_price
    cart.quantity = total_quantity
    return cart

@app.get("/cart", response_model=List[Cart])
def get_carts(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0.0),
    max_price: Optional[float] = Query(None, ge=0.0),
    min_quantity: Optional[int] = Query(None, ge=0),
    max_quantity: Optional[int] = Query(None, ge=0),
):
    carts_list = list(carts_db.values())
    filtered_carts = []

    for cart in carts_list:
        total_price = 0.0
        total_quantity = 0
        for cart_item in cart.items:
            item = items_db.get(cart_item.id)
            if item is None:
                cart_item.available = False
            else:
                cart_item.available = not item.deleted
                cart_item.name = item.name
                if not item.deleted:
                    total_price += item.price * cart_item.quantity
                    total_quantity += cart_item.quantity
        cart.price = total_price
        cart.quantity = total_quantity
        if min_price is not None and cart.price < min_price:
            continue
        if max_price is not None and cart.price > max_price:
            continue
        if min_quantity is not None and cart.quantity < min_quantity:
            continue
        if max_quantity is not None and cart.quantity > max_quantity:
            continue
        filtered_carts.append(cart)
    return filtered_carts[offset:offset+limit]

@app.post("/cart/{cart_id}/add/{item_id}")
def add_item_to_cart(
    cart_id: int = Path(..., ge=0),
    item_id: int = Path(..., ge=0),
):
    cart = carts_db.get(cart_id)
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    item = items_db.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            break
    else:
        cart_item = CartItem(id=item_id, name=item.name, quantity=1, available=not item.deleted)
        cart.items.append(cart_item)
    total_price = 0.0
    total_quantity = 0
    for cart_item in cart.items:
        item_db = items_db.get(cart_item.id)
        if item_db and not item_db.deleted:
            total_price += item_db.price * cart_item.quantity
            total_quantity += cart_item.quantity
    cart.price = total_price
    cart.quantity = total_quantity
    return {"detail": "Item added to cart"}

@app.post("/item", status_code=201)
def create_item(item_data: ItemCreate):
    global items_id_counter
    item_id = items_id_counter
    items_id_counter += 1
    item = Item(id=item_id, name=item_data.name, price=item_data.price, deleted=False)
    items_db[item_id] = item
    headers = {"Location": f"/item/{item_id}"}
    return JSONResponse(content=item.dict(), status_code=201, headers=headers)

@app.get("/item/{id}", response_model=Item)
def get_item(id: int = Path(..., ge=0)):
    item = items_db.get(id)
    if item is None or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/item", response_model=List[Item])
def get_items(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0.0),
    max_price: Optional[float] = Query(None, ge=0.0),
    show_deleted: bool = Query(False),
):
    items_list = list(items_db.values())
    filtered_items = []
    for item in items_list:
        if not show_deleted and item.deleted:
            continue
        if min_price is not None and item.price < min_price:
            continue
        if max_price is not None and item.price > max_price:
            continue
        filtered_items.append(item)
    return filtered_items[offset:offset+limit]

@app.put("/item/{id}", response_model=Item)
def replace_item(
    id: int = Path(..., ge=0),
    item_data: ItemUpdate = Body(...),
):
    item = items_db.get(id)
    if item is None or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    item.name = item_data.name
    item.price = item_data.price
    return item

@app.patch("/item/{id}", response_model=Item)
def update_item(
    id: int = Path(..., ge=0),
    item_data: ItemPatch = Body(...),
):
    item = items_db.get(id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.deleted:
        return Response(status_code=304)
    if item_data.name is not None:
        item.name = item_data.name
    if item_data.price is not None:
        item.price = item_data.price
    return item

@app.delete("/item/{id}")
def delete_item(id: int = Path(..., ge=0)):
    item = items_db.get(id)
    if item is None or item.deleted:
        return {"detail": "Item deleted"}
    item.deleted = True
    return {"detail": "Item deleted"}
