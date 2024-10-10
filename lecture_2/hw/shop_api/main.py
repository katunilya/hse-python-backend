from fastapi import FastAPI, HTTPException
from starlette import status
from starlette.responses import JSONResponse

from .models import Item, Cart, CartItem
from typing import List
from pydantic import BaseModel, conint, condecimal

app = FastAPI(title="Shop API")

carts = {}
items = {}

item_id_counter = 1
cart_id_counter = 1


class CreateItemRequest(BaseModel):
    name: str
    price: float


@app.post("/cart", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_cart():
    global cart_id_counter
    cart = Cart(id=cart_id_counter, price=0)
    carts[cart_id_counter] = cart
    cart_id_counter += 1
    return JSONResponse(
        content={"id": cart.id},
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"/cart/{cart.id}"}
    )


@app.get("/cart/{cart_id}", response_model=dict)
def get_cart(cart_id: int):
    cart = carts.get(cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart_price = sum(cart_item.quantity * items[cart_item.item_id].price for cart_item in cart.items)

    return {
        "id": cart.id,
        "items": [
            {
                "id": cart_item.id,
                "name": cart_item.name,
                "quantity": cart_item.quantity,
                "available": cart_item.available
            }
            for cart_item in cart.items
        ],
        "price": cart_price
    }


@app.get("/cart", response_model=List[dict])
def list_carts(
        offset: conint(ge=0) = 0,
        limit: conint(gt=0, le=100) = 10,
        min_price: condecimal(gt=0) = None,
        max_price: condecimal(gt=0) = None,
        min_quantity: conint(ge=0) = None,
        max_quantity: conint(ge=0) = None
):

    filtered_carts = list(carts.values())

    # Фильтрация по цене
    if min_price is not None:
        filtered_carts = [cart for cart in filtered_carts if cart.price >= min_price]
    if max_price is not None:
        filtered_carts = [cart for cart in filtered_carts if cart.price <= max_price]

    # Фильтрация по количеству товаров в корзинах
    if min_quantity is not None:
        filtered_carts = [
            cart for cart in filtered_carts
            if sum(cart_item.quantity for cart_item in cart.items) >= min_quantity
        ]
    if max_quantity is not None:
        filtered_carts = [
            cart for cart in filtered_carts
            if sum(cart_item.quantity for cart_item in cart.items) <= max_quantity
        ]

    # Преобразование объектов в словари
    return [cart.dict() for cart in filtered_carts[offset:offset + limit]]


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

    cart.price = sum(cart_item.quantity * items[cart_item.item_id].price for cart_item in cart.items)
    return {"message": "Item added to cart"}


@app.post("/item", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_item(item_data: CreateItemRequest):
    global item_id_counter
    item = Item(id=item_id_counter, name=item_data.name, price=item_data.price, deleted=False)
    items[item_id_counter] = item
    item_id_counter += 1
    return {
        "id": item.id,
        "name": item.name,  # Добавляем имя
        "price": item.price  # Добавляем цену
    }


@app.get("/item/{id}", response_model=dict)
def get_item(id: int):
    item = items.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found or deleted")

    return {
        'id': item.id,
        'name': item.name,
        'price': item.price,

    }


@app.get("/item", response_model=List[dict])
def list_items(offset: int = 0, limit: int = 10, show_deleted: bool = False, min_price: float = None,
               max_price: float = None):

    if limit <= 0:
        raise HTTPException(status_code=422, detail="Limit must be more than 0")

    if min_price is not None and min_price < 0:
        raise HTTPException(status_code=422, detail="min_price must be non-negative")
    if max_price is not None and max_price < 0:
        raise HTTPException(status_code=422, detail="max_price must be non-negative")

    if offset < 0:
        raise HTTPException(status_code=422, detail="offset must be more than 0")

    filtered_items = [item for item in items.values() if show_deleted or not item.deleted]

    if min_price is not None:
        filtered_items = [item for item in filtered_items if item.price >= min_price]

    if max_price is not None:
        filtered_items = [item for item in filtered_items if item.price <= max_price]

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


@app.put("/item/{id}", response_model=dict)
def update_item(id: int, item_data: CreateItemRequest):
    item = items.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found or deleted")

    item.name = item_data.name
    item.price = item_data.price

    return {
        "id": item.id,
        "name": item.name,
        "price": item.price
    }


@app.patch("/item/{id}", response_model=dict)
def partial_update_item(id: int, item_data: dict):
    item = items.get(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.deleted:
        return JSONResponse(status_code=status.HTTP_304_NOT_MODIFIED, content={})

    if "deleted" in item_data:
        raise HTTPException(status_code=422, detail="Field 'deleted' cannot be updated")

    allowed_fields = {"name", "price"}
    if any(field not in allowed_fields for field in item_data):
        raise HTTPException(status_code=422, detail="Unknown field in update request")

    # Обновляем поля
    if "name" in item_data:
        item.name = item_data["name"]
    if "price" in item_data:
        item.price = item_data["price"]

    return {
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "deleted": item.deleted
    }
