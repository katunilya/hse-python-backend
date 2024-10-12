from http import HTTPStatus
from typing import List, Optional

from fastapi import FastAPI, APIRouter, HTTPException, Response

from lecture_2.hw.shop_api.models import Cart, Item, ItemDto, DEFAULT_ITEM_DTO_FIELDS, ItemCart

items = []
carts = []

app = FastAPI(title="Shop API")

@app.post("/cart", status_code=HTTPStatus.CREATED)
def create_cart(response: Response):
    id = len(carts) + 1
    cart = Cart(id=id)
    carts.append(cart)
    # as REST states one should provide uri to newly created resource in location header
    response.headers["location"] = f"/cart/{cart.id}"
    return cart

@app.get("/cart/{id}", response_model=Cart)
def get_cart(id: int):
    for cart in carts:
        if cart.id == id:
            return cart
    raise HTTPException(detail="Cart not found", status_code=HTTPStatus.NOT_FOUND)

@app.post("/item", status_code=HTTPStatus.CREATED)
def add_item(item: ItemDto, response: Response):
    id = len(items) + 1
    item = Item(id=id, name=item.name, price=item.price, deleted = False)
    items.append(item)
    # as REST states one should provide uri to newly created resource in location header
    response.headers["location"] = f"/item/{item.id}"
    return item

@app.get("/item/{id}", response_model=Item)
def get_item(id: int):
    for item in items:
        if item.id == id and not item.deleted:
            return item
    raise HTTPException( detail="Item not found", status_code=HTTPStatus.NOT_FOUND)

@app.put("/item/{id}", response_model=Item)
def update_item(id: int, item: ItemDto):
    for i, current in enumerate(items):
        if current.id == id:
            new_item = Item(id=id, name=item.name, price=item.price)
            items[i] = new_item
            return new_item
    raise HTTPException( detail="Item not found", status_code=HTTPStatus.NOT_FOUND)

@app.patch("/item/{id}", response_model=Item)
def patch_item(id: int, updated_fields: dict):

    for k in updated_fields.keys():
        if not(k in DEFAULT_ITEM_DTO_FIELDS):
            raise HTTPException(detail=f"Unexpected field {k}", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    for i, current in enumerate(items):
        if current.id == id:
            if current.deleted:
                raise HTTPException(detail="Cannot change deleted item", status_code=HTTPStatus.NOT_MODIFIED)
            if 'deleted' in updated_fields:
                raise HTTPException(detail="Cannot change 'deleted' field", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
            item_data = current.dict()
            item_data.update(updated_fields)
            patched_item = Item(**item_data)
            items[i] = patched_item
            return patched_item
    raise HTTPException( detail="Item not found", status_code=HTTPStatus.NOT_FOUND)

@app.delete("/item/{id}")
def delete_item(id: int):
    for item in items:
        if item.id == id:
            item.deleted = True
            return {"message": "Item deleted"}
    raise HTTPException( detail="Item not found", status_code=HTTPStatus.NOT_FOUND)

@app.get("/item", response_model=List[Item])
def list_items(
    offset: int = 0, limit: int = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    show_deleted: bool = False
):
    filtered_items = []
    if offset < 0:
        raise HTTPException(detail="Offset should be positive", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if limit <= 0:
        raise HTTPException(detail="Limit should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if not(min_price is None) and min_price < 0:
        raise HTTPException(detail="min_price should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if not(max_price is None) and max_price < 0:
        raise HTTPException(detail="max_price should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)

    for i in range(offset, len(items)):
        if len(filtered_items) == limit:
            break
        item = items[i]
        if (show_deleted or not item.deleted) and (min_price is None or item.price >= min_price) and \
                (max_price is None or item.price <= max_price):
            filtered_items.append(item)

    return filtered_items

@app.get("/cart", response_model=List[Cart])
def list_cart(
    offset: int = 0, limit: int = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_quantity: Optional[int] = None,
    max_quantity: Optional[int] = None
):
    filtered_carts = []
    if offset < 0:
        raise HTTPException(detail="Offset should be positive", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if limit <= 0:
        raise HTTPException(detail="Limit should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if not(min_price is None) and min_price < 0:
        raise HTTPException(detail="min_price should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if not(max_price is None) and max_price < 0:
        raise HTTPException(detail="max_price should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if not(min_quantity is None) and min_quantity < 0:
        raise HTTPException(detail="min_quantity should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if not(max_quantity is None) and max_quantity < 0:
        raise HTTPException(detail="max_quantity should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)

    for i in range(offset, len(carts)):
        if len(filtered_carts) == limit:
            break
        cart = carts[i]
        if (min_price is None or cart.price >= min_price) and \
            (max_price is None or cart.price <= max_price) and \
            (min_quantity is None or sum(item.quantity for item in cart.items) >= min_quantity) and \
            (max_quantity is None or sum(item.quantity for item in cart.items) <= max_quantity):
                filtered_carts.append(cart)


    return filtered_carts

@app.post("/cart/{cart_id}/add/{item_id}", response_model=Cart)
def add_item_to_cart(cart_id: int, item_id: int):
    for cart in carts:
        if cart.id == cart_id:
            for item in items:
                if item.id == item_id and not item.deleted:
                    for current_item in cart.items:
                        if current_item.id == item_id:
                            current_item.quantity += 1
                            cart.price += item.price
                            return cart
                    cart.items.append(ItemCart(id=item.id, name=item.name, quantity=1, available=True))
                    cart.price += item.price
                    return cart
            raise HTTPException(detail="Item not found", status_code=HTTPStatus.NOT_FOUND,)
    raise HTTPException(detail="Cart not found", status_code=HTTPStatus.NOT_FOUND,)