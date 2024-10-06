from fastapi import FastAPI
from http import HTTPStatus
from fastapi import HTTPException, Response

from lecture_2.hw.shop_api.models import Cart, CartItem, Item, ItemDto
from lecture_2.hw.shop_api.storage import carts, items
from lecture_2.hw.shop_api.utils import generate_id

from typing import Optional

app = FastAPI(title="Shop API")

@app.post("/cart", status_code=HTTPStatus.CREATED)
def create_cart(response: Response):
    cart_id = generate_id()
    carts[cart_id] = Cart(id=cart_id)
    response.headers['location'] = f"/cart/{cart_id}"
    return {'id': cart_id}


@app.get("/cart/{id}")
def get_cart(id: int):
    cart = carts.get(id)
    if not cart:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")
    return cart


@app.get("/cart")
def get_carts(offset: int = 0, limit: int = 10, min_price: Optional[float] = None, max_price: Optional[float] = None, min_quantity: Optional[int] = None, max_quantity: Optional[int] = None):
    if (offset < 0):
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="offset is negative")
    
    if (limit <= 0):
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="offset isn't positive")
    
    if (min_price and min_price < 0):
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="min_price is negative")
    
    if (max_price and max_price < 0):
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="max_price is negative")
    
    if (min_quantity and min_quantity < 0):
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="min_quantity is negative")
    
    if (max_quantity and max_quantity < 0):
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="max_quantity is negative")
    
    result = [
        cart for cart in carts.values()
        if (min_price is None or cart.price >= min_price)
        and (max_price is None or cart.price <= max_price)
        and (min_quantity is None or sum(item.quantity for item in cart.items) >= min_quantity)
        and (max_quantity is None or sum(item.quantity for item in cart.items) <= max_quantity)
    ]
    return result[offset:offset+limit]


@app.post("/cart/{cart_id}/add/{item_id}")
def add_item_to_cart(cart_id: int, item_id: int):
    cart = carts.get(cart_id)
    item = items.get(item_id)

    if not cart:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")
    if not item or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            break
    else:
        cart.items.append(CartItem(id=item_id, name=item.name, quantity=1, available=not item.deleted))

    cart.price = sum(item.quantity * items[item.id].price for item in cart.items)


@app.post("/item", status_code=HTTPStatus.CREATED)
def add_item(item_dto: ItemDto, response: Response):
    id = generate_id()
    item = Item(id=id, name=item_dto.name, price=item_dto.price, deleted = False)
    items[id] = item
    response.headers["location"] = f"/item/{item.id}"
    return item


@app.get("/item/{id}")
def get_item(id: int):
    item = items.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    return item


@app.get("/item")
def get_items(offset: int = 0, limit: int = 10, min_price: Optional[float] = None, max_price: Optional[float] = None, show_deleted: bool = False):
    if (offset < 0):
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="offset is negative")
    
    if (limit <= 0):
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="offset isn't positive")
    
    if (min_price and min_price < 0):
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="min_price is negative")
    
    if (max_price and max_price < 0):
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="max_price is negative")
    
    result = [
        item for item in items.values()
        if (show_deleted or not item.deleted)
        and (min_price is None or item.price >= min_price)
        and (max_price is None or item.price <= max_price)
    ]
    return result[offset:offset+limit]


@app.put("/item/{id}")
def update_item(id: int, updated_item: ItemDto):
    item = items.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    items[id] = Item(id=id, name=updated_item.name, price=updated_item.price)
    return items[id]


@app.patch("/item/{id}")
def partial_update_item(id: int, updated_data: dict):
    item = items.get(id)
    if not item or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, detail="Item not found")
    
    for key, value in updated_data.items():
        if not key in item.__dict__.keys() or key == "deleted" or key == "id":
            raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, "Unavailable key")
    
    for key, value in updated_data.items():
        setattr(item, key, value)

    return item


@app.delete("/item/{id}")
def delete_item(id: int):
    item = items.get(id)
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    item.deleted = True