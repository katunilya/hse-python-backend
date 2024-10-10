from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel
from typing import List, Dict, Optional
from fastapi.responses import JSONResponse
from threading import Lock

app = FastAPI()

class ItemInput(BaseModel):
    name: str
    price: float

    class Config:
        extra = "forbid"

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

    class Config:
        extra = "forbid"

class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False

class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

class Cart(BaseModel):
    id: int
    items: List[CartItem]
    price: float

# In-memory databases
items_db: Dict[int, Item] = {}
carts_db: Dict[int, Cart] = {}

# ID counters and locks
item_id_counter = 0
cart_id_counter = 0
item_id_lock = Lock()
cart_id_lock = Lock()

# Item endpoints
@app.post("/item", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemInput):
    global item_id_counter
    with item_id_lock:
        item_id_counter += 1
        item_id = item_id_counter
    new_item = Item(id=item_id, name=item.name, price=item.price)
    items_db[item_id] = new_item
    response = JSONResponse(status_code=status.HTTP_201_CREATED, content=new_item.dict())
    response.headers["Location"] = f"/item/{item_id}"
    return response

@app.get("/item/{id}")
def get_item(id: int):
    item = items_db.get(id)
    if item and not item.deleted:
        return item
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

@app.get("/item")
def get_items(
    offset: int = 0,
    limit: int = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    show_deleted: bool = False,
):
    if offset < 0 or limit <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid offset or limit")
    items = list(items_db.values())
    if not show_deleted:
        items = [item for item in items if not item.deleted]
    if min_price is not None:
        if min_price < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid min_price")
        items = [item for item in items if item.price >= min_price]
    if max_price is not None:
        if max_price < 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid max_price")
        items = [item for item in items if item.price <= max_price]
    items = items[offset : offset + limit]
    return items

@app.put("/item/{id}")
def replace_item(id: int, item: ItemInput):
    existing_item = items_db.get(id)
    if not existing_item or existing_item.deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    existing_item.name = item.name
    existing_item.price = item.price
    items_db[id] = existing_item
    return existing_item

@app.patch("/item/{id}")
def update_item(id: int, item: ItemUpdate):
    existing_item = items_db.get(id)
    if not existing_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if existing_item.deleted:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)
    update_data = item.dict(exclude_unset=True)
    if not update_data:
        return existing_item
    if "deleted" in update_data:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Cannot modify 'deleted' field")
    if "name" in update_data:
        existing_item.name = update_data["name"]
    if "price" in update_data:
        existing_item.price = update_data["price"]
    items_db[id] = existing_item
    return existing_item

@app.delete("/item/{id}")
def delete_item(id: int):
    existing_item = items_db.get(id)
    if not existing_item:
        return
    existing_item.deleted = True
    items_db[id] = existing_item
    return

# Cart endpoints
@app.post("/cart", status_code=status.HTTP_201_CREATED)
def create_cart():
    global cart_id_counter
    with cart_id_lock:
        cart_id_counter += 1
        cart_id = cart_id_counter
    new_cart = Cart(id=cart_id, items=[], price=0.0)
    carts_db[cart_id] = new_cart
    response = JSONResponse(status_code=status.HTTP_201_CREATED, content={"id": cart_id})
    response.headers["Location"] = f"/cart/{cart_id}"
    return response

@app.get("/cart/{id}")
def get_cart(id: int):
    cart = carts_db.get(id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    total_price = 0.0
    for cart_item in cart.items:
        item = items_db.get(cart_item.id)
        if item:
            cart_item.name = item.name
            cart_item.available = not item.deleted
            if cart_item.available:
                total_price += item.price * cart_item.quantity
        else:
            cart_item.available = False
    cart.price = total_price
    return {"id": cart.id, "items": [item.dict() for item in cart.items], "price": cart.price}

@app.post("/cart/{cart_id}/add/{item_id}")
def add_item_to_cart(cart_id: int, item_id: int):
    cart = carts_db.get(cart_id)
    if not cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    item = items_db.get(item_id)
    if not item or item.deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found or unavailable")
    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            break
    else:
        cart_item = CartItem(id=item_id, name=item.name, quantity=1, available=not item.deleted)
        cart.items.append(cart_item)
    return

@app.get("/cart")
def get_carts(
    offset: int = 0,
    limit: int = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_quantity: Optional[int] = None,
    max_quantity: Optional[int] = None,
):
    if offset < 0 or limit <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid offset or limit")
    if min_price is not None and min_price < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid min_price")
    if max_price is not None and max_price < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid max_price")
    if min_quantity is not None and min_quantity < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid min_quantity")
    if max_quantity is not None and max_quantity < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid max_quantity")
    carts = list(carts_db.values())
    result_carts = []
    for cart in carts:
        total_price = 0.0
        total_quantity = 0
        for cart_item in cart.items:
            item = items_db.get(cart_item.id)
            if item and not item.deleted:
                cart_item.available = True
                cart_item.name = item.name
                total_price += item.price * cart_item.quantity
                total_quantity += cart_item.quantity
            else:
                cart_item.available = False
        cart.price = total_price
        if min_price is not None and cart.price < min_price:
            continue
        if max_price is not None and cart.price > max_price:
            continue
        if min_quantity is not None and total_quantity < min_quantity:
            continue
        if max_quantity is not None and total_quantity > max_quantity:
            continue
        result_carts.append(cart)
    result_carts = result_carts[offset : offset + limit]
    carts_response = []
    for cart in result_carts:
        carts_response.append({"id": cart.id, "items": [item.dict() for item in cart.items], "price": cart.price})
    return carts_response
