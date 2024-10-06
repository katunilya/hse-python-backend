from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List


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


app = FastAPI(title="Shop API")

# База данных в памяти (для примера)
items_db = {}
carts_db = {}


# --- Item Endpoints ---
@app.post("/item", response_model=Item)
def create_item(item: Item):
    if item.id in items_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    items_db[item.id] = item
    return item


@app.get("/item/{id}", response_model=Item)
def get_item(id: int):
    item = items_db.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.get("/item", response_model=List[Item])
def get_items(offset: int = 0, limit: int = 10, min_price: Optional[float] = None, max_price: Optional[float] = None,
              show_deleted: bool = False):
    items = [item for item in items_db.values() if (show_deleted or not item.deleted)]

    if min_price is not None:
        items = [item for item in items if item.price >= min_price]
    if max_price is not None:
        items = [item for item in items if item.price <= max_price]

    return items[offset:offset + limit]


@app.put("/item/{id}", response_model=Item)
def update_item(id: int, item: Item):
    if id not in items_db or items_db[id].deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db[id] = item
    return item


@app.patch("/item/{id}", response_model=Item)
def patch_item(id: int, item: Item):
    stored_item = items_db.get(id)
    if not stored_item or stored_item.deleted:
        raise HTTPException(status_code=404, detail="Item not found")

    stored_item_data = stored_item.dict()
    updated_item = stored_item_data | item.dict(exclude_unset=True)
    items_db[id] = Item(**updated_item)
    return items_db[id]


@app.delete("/item/{id}")
def delete_item(id: int):
    item = items_db.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    item.deleted = True
    return {"message": "Item marked as deleted"}


# --- Cart Endpoints ---
@app.post("/cart", response_model=int)
def create_cart():
    new_cart_id = max(carts_db.keys(), default=0) + 1
    carts_db[new_cart_id] = Cart(id=new_cart_id, items=[], price=0.0)
    return new_cart_id


@app.get("/cart/{id}", response_model=Cart)
def get_cart(id: int):
    cart = carts_db.get(id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart


@app.get("/cart", response_model=List[Cart])
def get_carts(offset: int = 0, limit: int = 10, min_price: Optional[float] = None, max_price: Optional[float] = None,
              min_quantity: Optional[int] = None, max_quantity: Optional[int] = None):
    carts = list(carts_db.values())

    if min_price is not None:
        carts = [cart for cart in carts if cart.price >= min_price]
    if max_price is not None:
        carts = [cart for cart in carts if cart.price <= max_price]
    if min_quantity is not None:
        carts = [cart for cart in carts if sum(item.quantity for item in cart.items) >= min_quantity]
    if max_quantity is not None:
        carts = [cart for cart in carts if sum(item.quantity for item in cart.items) <= max_quantity]

    return carts[offset:offset + limit]


@app.post("/cart/{cart_id}/add/{item_id}", response_model=Cart)
def add_item_to_cart(cart_id: int, item_id: int):
    cart = carts_db.get(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    item = items_db.get(item_id)
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found")

    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            break
    else:
        cart.items.append(CartItem(id=item.id, name=item.name, quantity=1, available=True))

    cart.price += item.price
    return cart