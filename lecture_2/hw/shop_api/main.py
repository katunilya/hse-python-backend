from fastapi import FastAPI, HTTPException
from models import Item, Cart, CartItem
from typing import List
from pydantic import BaseModel

app = FastAPI(title="Shop API")
# Хранилище данных
carts = {}
items = {}

# Счётчики для ID
item_id_counter = 1
cart_id_counter = 1


# Pydantic-схемы для валидации запросов
class CreateItemRequest(BaseModel):
    name: str
    price: float


# API для работы с корзинами
@app.post("/cart", response_model=dict)
def create_cart():
    global cart_id_counter
    cart = Cart(id=cart_id_counter)
    carts[cart_id_counter] = cart
    cart_id_counter += 1
    return {"id": cart.id}


@app.get("/cart/{cart_id}", response_model=dict)
def get_cart(cart_id: int):
    cart = carts.get(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    return {
        "id": cart.id,
        "items": [{
            "id": item.id,
            "name": item.name,
            "quantity": item.quantity,
            "available": item.available
        } for item in cart.items],
        "price": cart.price
    }


@app.get("/cart", response_model=List[dict])
def list_carts(offset: int = 0, limit: int = 10):
    all_carts = list(carts.values())[offset:offset + limit]
    return [{"id": cart.id, "price": cart.price} for cart in all_carts]


@app.post("/cart/{cart_id}/add/{item_id}", response_model=dict)
def add_item_to_cart(cart_id: int, item_id: int):
    cart = carts.get(cart_id)
    item = items.get(item_id)

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found or deleted")

    cart_item = next((ci for ci in cart.items if ci.item_id == item.id), None)

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(id=len(cart.items) + 1, item_id=item.id, name=item.name, quantity=1,
                             available=not item.deleted)
        cart.items.append(cart_item)

    cart.price += item.price
    return {"message": "Item added to cart"}


# API для работы с товарами
@app.post("/item", response_model=dict)
def create_item(item_data: CreateItemRequest):
    global item_id_counter
    item = Item(id=item_id_counter, name=item_data.name, price=item_data.price)
    items[item_id_counter] = item
    item_id_counter += 1
    return {"id": item.id}


@app.get("/item/{id}", response_model=dict)
def get_item(id: int):
    item = items.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found or deleted")

    return {
        'id': item.id,
        'name': item.name,
        'price': item.price,
        'deleted': item.deleted
    }


@app.get("/item", response_model=List[dict])
def list_items(offset: int = 0, limit: int = 10, show_deleted: bool = False):
    filtered_items = [item for item in items.values() if show_deleted or not item.deleted]
    return [{
        'id': item.id,
        'name': item.name,
        'price': item.price,
        'deleted': item.deleted
    } for item in filtered_items[offset:offset + limit]]


@app.delete("/item/{id}", response_model=dict)
def delete_item(id: int):
    item = items.get(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.deleted = True
    return {"message": "Item marked as deleted"}