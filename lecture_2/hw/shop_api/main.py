from typing import List, Optional


from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, ConfigDict
from http import HTTPStatus


class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False

class ItemCreate(BaseModel):
    name: str
    price: float

class ItemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = None
    price: Optional[float] = None

class ItemCart(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

class Cart(BaseModel):
    id: int
    items: List[ItemCart] = []
    price: float = 0.0


items = {}
carts = {}

app = FastAPI(title="Shop API")



@app.post("/item", status_code=HTTPStatus.CREATED)
def add_item(item: ItemCreate, response: Response):
    new_id = len(items) + 1
    new_item = Item(id=new_id, name=item.name, price=item.price)
    items[new_id] = new_item
    response.headers["location"] = f"/item/{new_id}"
    return new_item


@app.get("/item/{id}", response_model=Item)
def get_item(id: int):
    item = items.get(id)
    if item is None or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    return item



@app.put("/item/{id}", response_model=Item)
def update_item(id: int, item: ItemCreate):
    item_to_update = items.get(id)
    if item_to_update is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    
    item_to_update.name, item_to_update.price = item.name, item.price
    items[id] = item_to_update
    return item_to_update


@app.patch("/item/{id}", response_model=Item)
def patch_item(id: int, item_update: ItemUpdate):
    item_to_update = items.get(id)
    if item_to_update is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    
    if item_to_update.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, detail="Can't path a deleted item")
    
    
    if item_update.name is not None:
        item_to_update.name = item_update.name
    if item_update.price is not None:
        item_to_update.price = item_update.price
    
    items[id] = item_to_update
    return item_to_update

@app.delete("/item/{id}")
def delete_item(id: int):
    item = items.get(id)
    if item is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    
    item.deleted = True
    items[id] = item
    return {"message": "Item deleted"}

@app.get("/item", response_model=List[Item])
def list_items(
    offset: int = 0, limit: int = 10,
    min_price: Optional[float] = None, max_price: Optional[float] = None,
    show_deleted: bool = False
):
    if offset < 0:
        raise HTTPException(detail="offset should be positive", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if limit <= 0:
        raise HTTPException(detail="limit should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if not min_price is None and min_price < 0:
        raise HTTPException(detail="min_price should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if not max_price is None and max_price < 0:
        raise HTTPException(detail="max_price should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)

    filtered_items = [
        item for item in items.values() if 
        (show_deleted or not item.deleted) and
        (min_price is None or item.price >= min_price) and
        (max_price is None or item.price <= max_price)
    ]
    return filtered_items[offset: offset + limit]

# Cart Endpoints
@app.post("/cart", status_code=HTTPStatus.CREATED)
def create_cart(response: Response):
    new_id = len(carts) + 1
    new_cart = Cart(id=new_id)
    carts[new_id] = new_cart
    response.headers["location"] = f"/cart/{new_id}"
    return new_cart

@app.get("/cart/{id}", response_model=Cart)
def get_cart(id: int):
    cart = carts.get(id)
    if cart is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")
    return cart

@app.get("/cart", response_model=List[Cart])
def list_carts(
    offset: int = 0, limit: int = 10,
    min_price: Optional[float] = None, max_price: Optional[float] = None,
    min_quantity: Optional[int] = None, max_quantity: Optional[int] = None
):
    if offset < 0:
        raise HTTPException(detail="offset should be positive", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if limit <= 0:
        raise HTTPException(detail="limit should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if not min_price is None and min_price < 0:
        raise HTTPException(detail="min_price should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if not max_price is None and max_price < 0:
        raise HTTPException(detail="max_price should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if not min_quantity is None and min_quantity < 0:
        raise HTTPException(detail="min_quantity should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if not max_quantity is None and max_quantity < 0:
        raise HTTPException(detail="max_quantity should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)


    filtered_carts = [
        cart for cart in carts.values() if 
        (min_price is None or cart.price >= min_price)  
        and (max_price is None or cart.price <= max_price)
        and (min_quantity is None or sum(item.quantity for item in cart.items) >= min_quantity)
        and (max_quantity is None or sum(item.quantity for item in cart.items) <= max_quantity)
    ]
    return filtered_carts[offset: offset + limit]

@app.post("/cart/{cart_id}/add/{item_id}", response_model=Cart)
def add_item_to_cart(cart_id: int, item_id: int):
    cart = carts.get(cart_id)
    if cart is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")
    
    item = items.get(item_id)
    if item is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            cart.price += item.price
            return cart

    cart.items.append(ItemCart(id=item.id, name=item.name, quantity=1, available=True))
    cart.price += item.price
    return cart
