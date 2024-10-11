from fastapi import FastAPI, HTTPException, status, Query, Response
from fastapi.responses import JSONResponse
from typing import Optional, Dict, List
from pydantic import BaseModel
from .models import Item, Cart, CartItem, ItemPost, ItemPatch
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Shop API")

Instrumentator().instrument(app).expose(app)

items: Dict[int, Item] = {}
carts: Dict[int, Cart] = {}


class CartResponse(BaseModel):
    id: int
    items: List[CartItem]
    price: float


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float


@app.post("/cart", status_code=status.HTTP_201_CREATED)
def create_cart():
    cart_id = len(carts) + 1
    carts[cart_id] = Cart(id=cart_id)
    return JSONResponse(content={"id": cart_id},
                        status_code=status.HTTP_201_CREATED,
                        headers={"Location": f"/cart/{cart_id}"})


@app.get("/cart/{id}", response_model=CartResponse)
def get_cart(id: int):
    if id not in carts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    cart = carts[id]
    # Обновляем доступность товаров
    for cart_item in cart.items:
        item = items.get(cart_item.id)
        cart_item.available = item is not None and not item.deleted
    return cart


@app.get("/cart", response_model=List[CartResponse])
def get_cart_list(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0.0),
    max_price: Optional[float] = Query(None, ge=0.0),
    min_quantity: Optional[int] = Query(None, ge=0),
    max_quantity: Optional[int] = Query(None, ge=0),
):
    filtered_carts = [cart for cart in list(carts.values())[offset:offset + limit]
                      if (min_price is None or cart.price >= min_price) and
                      (max_price is None or cart.price <= max_price) and
                      (min_quantity is None or sum(item.quantity for item in cart.items) >= min_quantity) and
                      (max_quantity is None or sum(item.quantity for item in cart.items) <= max_quantity)]
    return filtered_carts


@app.post("/cart/{cart_id}/add/{item_id}")
def add_to_cart(cart_id: int, item_id: int):
    if cart_id not in carts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    if item_id not in items or items[item_id].deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found or deleted")

    item = items[item_id]
    cart = carts[cart_id]
    for cart_item in cart.items:
        if cart_item.id == item.id:
            cart_item.quantity += 1
            break
    else:
        cart.items.append(CartItem(id=item.id, name=item.name, quantity=1, available=not item.deleted))
    cart.price += item.price
    return cart


@app.post("/item", status_code=status.HTTP_201_CREATED, response_model=ItemResponse)
def create_item(item: ItemPost):
    item_id = len(items) + 1
    new_item = Item(id=item_id, name=item.name, price=item.price)
    items[item_id] = new_item
    return JSONResponse(
        content={"id": new_item.id, "name": new_item.name, "price": new_item.price},
        status_code=status.HTTP_201_CREATED,
        headers={"Location": f"/item/{item_id}"})


@app.get("/item/{id}", response_model=ItemResponse, status_code=status.HTTP_200_OK)
def get_item(id: int):
    if id not in items or items[id].deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return items[id]


@app.get("/item", response_model=List[ItemResponse])
def get_item_list(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0.0),
    max_price: Optional[float] = Query(None, ge=0.0),
    show_deleted: bool = False
):
    filtered_items = [item for item in list(items.values())[offset:offset + limit]
                      if (show_deleted or not item.deleted) and
                      (min_price is None or item.price >= min_price) and
                      (max_price is None or item.price <= max_price)]
    return filtered_items


@app.put("/item/{id}", response_model=ItemResponse)
def update_item(id: int, item: ItemPost):
    if id not in items or items[id].deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    new_item = Item(id=id, name=item.name, price=item.price)
    items[id] = new_item
    return new_item


@app.patch("/item/{id}", response_model=ItemResponse)
def patch_item(id: int, item_patch: ItemPatch, response: Response):
    item = items.get(id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.deleted:
        # Возвращаем 304 Not Modified без тела ответа
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)

    update_data = item_patch.model_dump(exclude_unset=True)
    if not update_data:
        return item  # Возвращаем текущий товар со статусом 200 OK

    for key, value in update_data.items():
        setattr(item, key, value)
    return item


@app.delete("/item/{id}")
def delete_item(id: int):
    item = items.get(id)
    if not item:
        return {"message": "Item not found, but this is treated as deleted"}
    if item.deleted:
        return {"message": "Item already deleted"}
    item.deleted = True
    return {"message": "Item marked as deleted"}
