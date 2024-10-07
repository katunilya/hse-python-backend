from http import HTTPStatus
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Response

from lecture_2.hw.shop_api.models import Cart, Item, ItemDto, DEFAULT_ITEM_DTO_FIELDS, ItemCart

app = FastAPI(title="Shop API")

items = []
carts = []

# Utility functions for repeated logic
def get_item_by_id(item_id: int) -> Optional[Item]:
    """Returns an item by its ID if found and not deleted."""
    for item in items:
        if item.id == item_id and not item.deleted:
            return item
    return None

def get_cart_by_id(cart_id: int) -> Optional[Cart]:
    """Returns a cart by its ID if found."""
    for cart in carts:
        if cart.id == cart_id:
            return cart
    return None

def validate_offset_limit(offset: int, limit: int):
    """Validates offset and limit query parameters."""
    if offset < 0:
        raise HTTPException(detail="Offset should be positive", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    if limit <= 0:
        raise HTTPException(detail="Limit should be more than 0", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)

# Endpoints
@app.post("/cart", status_code=HTTPStatus.CREATED)
def create_cart(response: Response):
    cart_id = len(carts) + 1
    cart = Cart(id=cart_id)
    carts.append(cart)
    response.headers["location"] = f"/cart/{cart_id}"
    return cart

@app.get("/cart/{id}", response_model=Cart)
def get_cart(id: int):
    cart = get_cart_by_id(id)
    if cart is None:
        raise HTTPException(detail="Cart not found", status_code=HTTPStatus.NOT_FOUND)
    return cart

@app.post("/item", status_code=HTTPStatus.CREATED)
def add_item(item: ItemDto, response: Response):
    item_id = len(items) + 1
    new_item = Item(id=item_id, name=item.name, price=item.price)
    items.append(new_item)
    response.headers["location"] = f"/item/{item_id}"
    return new_item

@app.get("/item/{id}", response_model=Item)
def get_item(id: int):
    item = get_item_by_id(id)
    if item is None:
        raise HTTPException(detail="Item not found", status_code=HTTPStatus.NOT_FOUND)
    return item

@app.put("/item/{id}", response_model=Item)
def update_item(id: int, item: ItemDto):
    for i, current_item in enumerate(items):
        if current_item.id == id:
            updated_item = Item(id=id, name=item.name, price=item.price)
            items[i] = updated_item
            return updated_item
    raise HTTPException(detail="Item not found", status_code=HTTPStatus.NOT_FOUND)

@app.patch("/item/{id}", response_model=Item)
def patch_item(id: int, updated_fields: dict):
    if any(k not in DEFAULT_ITEM_DTO_FIELDS for k in updated_fields.keys()):
        raise HTTPException(detail=f"Unexpected field", status_code=HTTPStatus.UNPROCESSABLE_ENTITY)

    for i, current_item in enumerate(items):
        if current_item.id == id:
            if current_item.deleted:
                raise HTTPException(detail="Cannot change deleted item", status_code=HTTPStatus.NOT_MODIFIED)
            
            current_item_data = current_item.dict()
            current_item_data.update(updated_fields)
            patched_item = Item(**current_item_data)
            items[i] = patched_item
            return patched_item
    raise HTTPException(detail="Item not found", status_code=HTTPStatus.NOT_FOUND)

@app.delete("/item/{id}")
def delete_item(id: int):
    item = get_item_by_id(id)
    if item:
        item.deleted = True
        return {"message": "Item deleted"}
    raise HTTPException(detail="Item not found", status_code=HTTPStatus.NOT_FOUND)

@app.get("/item", response_model=List[Item])
def list_items(
    offset: int = 0, limit: int = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    show_deleted: bool = False
):
    validate_offset_limit(offset, limit)

    filtered_items = [
        item for item in items
        if (show_deleted or not item.deleted)
        and (min_price is None or item.price >= min_price)
        and (max_price is None or item.price <= max_price)
    ]
    
    return filtered_items[offset:offset + limit]

@app.get("/cart", response_model=List[Cart])
def list_cart(
    offset: int = 0, limit: int = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_quantity: Optional[int] = None,
    max_quantity: Optional[int] = None
):
    validate_offset_limit(offset, limit)

    filtered_carts = [
        cart for cart in carts
        if (min_price is None or cart.price >= min_price)
        and (max_price is None or cart.price <= max_price)
        and (min_quantity is None or sum(item.quantity for item in cart.items) >= min_quantity)
        and (max_quantity is None or sum(item.quantity for item in cart.items) <= max_quantity)
    ]
    
    return filtered_carts[offset:offset + limit]

@app.post("/cart/{cart_id}/add/{item_id}", response_model=Cart)
def add_item_to_cart(cart_id: int, item_id: int):
    cart = get_cart_by_id(cart_id)
    if cart is None:
        raise HTTPException(detail="Cart not found", status_code=HTTPStatus.NOT_FOUND)

    item = get_item_by_id(item_id)
    if item is None:
        raise HTTPException(detail="Item not found", status_code=HTTPStatus.NOT_FOUND)

    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            cart.price += item.price
            return cart

    cart.items.append(ItemCart(id=item.id, name=item.name, quantity=1, available=True))
    cart.price += item.price
    return cart
