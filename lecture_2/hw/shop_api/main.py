from fastapi import FastAPI, HTTPException, Query, status
from typing import List, Optional, Any
from pydantic import BaseModel, Field

app = FastAPI(title="Shop API")

# Данные для товаров и корзин
items = []
carts = []
item_counter = 1
cart_counter = 1


# Модели для данных
class Item(BaseModel):
    id: int
    name: str
    price: float = Field(gt=0, description="Price must be greater than zero")
    deleted: bool = False


class CartItem(BaseModel):
    id: int
    name: str
    quantity: int = Field(ge=1, description="Quantity must be at least 1")
    available: bool = True


class Cart(BaseModel):
    id: int
    items: List[CartItem]
    price: float


# RPC: Создание новой корзины
@app.post("/cart", status_code=status.HTTP_201_CREATED)
def create_cart():
    global cart_counter
    cart = {"id": cart_counter, "items": [], "price": 0.0}
    carts.append(cart)
    cart_counter += 1
    return {"id": cart["id"], "location": f"/cart/{cart['id']}"}


# Получение корзины по id
@app.get("/cart/{cart_id}")
def get_cart(cart_id: int):
    cart = next((c for c in carts if c["id"] == cart_id), None)
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart


# Получение списка корзин с фильтрацией
@app.get("/cart")
def list_carts(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0.0),
    max_price: Optional[float] = Query(None, ge=0.0),
    min_quantity: Optional[int] = Query(None, ge=0),
    max_quantity: Optional[int] = Query(None, ge=0),
):
    filtered_carts = carts

    # Фильтрация по цене
    if min_price is not None:
        filtered_carts = [c for c in filtered_carts if c["price"] >= min_price]
    if max_price is not None:
        filtered_carts = [c for c in filtered_carts if c["price"] <= max_price]

    # Фильтрация по количеству товаров
    if min_quantity is not None:
        filtered_carts = [
            c
            for c in filtered_carts
            if sum(item["quantity"] for item in c["items"]) >= min_quantity
        ]
    if max_quantity is not None:
        filtered_carts = [
            c
            for c in filtered_carts
            if sum(item["quantity"] for item in c["items"]) <= max_quantity
        ]

    return filtered_carts[offset : offset + limit]


# Добавление товара в корзину
@app.post("/cart/{cart_id}/add/{item_id}")
def add_item_to_cart(cart_id: int, item_id: int):
    cart = next((c for c in carts if c["id"] == cart_id), None)
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")

    item = next((i for i in items if i["id"] == item_id and not i["deleted"]), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found or deleted")

    for cart_item in cart["items"]:
        if cart_item["id"] == item["id"]:
            cart_item["quantity"] += 1
            break
    else:
        cart["items"].append(
            {"id": item["id"], "name": item["name"], "quantity": 1, "available": True}
        )

    cart["price"] = sum(
        cart_item["quantity"] * item["price"] for cart_item in cart["items"]
    )
    return cart


# Добавление нового товара
@app.post("/item", status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    global item_counter
    new_item = item.dict()
    new_item["id"] = item_counter
    item_counter += 1
    items.append(new_item)
    return new_item


# Получение товара по id
@app.get("/item/{item_id}")
def get_item(item_id: int):
    item = next((i for i in items if i["id"] == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# Получение списка товаров с фильтрацией
@app.get("/item")
def list_items(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0.0),
    max_price: Optional[float] = Query(None, ge=0.0),
    show_deleted: bool = False,
):
    filtered_items = items

    if min_price is not None:
        filtered_items = [i for i in filtered_items if i["price"] >= min_price]
    if max_price is not None:
        filtered_items = [i for i in filtered_items if i["price"] <= max_price]
    if not show_deleted:
        filtered_items = [i for i in filtered_items if not i["deleted"]]

    return filtered_items[offset : offset + limit]


# Замена товара
@app.put("/item/{item_id}")
def replace_item(item_id: int, new_item: Item):
    for idx, item in enumerate(items):
        if item["id"] == item_id:
            new_item_data = new_item.dict()
            new_item_data["id"] = item_id
            items[idx] = new_item_data
            return items[idx]
    raise HTTPException(status_code=404, detail="Item not found")


# Частичное обновление товара
@app.patch("/item/{item_id}")
def update_item(item_id: int, updated_item: Any):
    item = next((i for i in items if i["id"] == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if "deleted" in updated_item:
        raise HTTPException(status_code=422, detail="Field 'deleted' cannot be updated")

    update_data = {k: v for k, v in updated_item.items() if k in ["name", "price"]}
    item.update(update_data)
    return item


# Удаление товара (пометка deleted)
@app.delete("/item/{item_id}")
def delete_item(item_id: int):
    item = next((i for i in items if i["id"] == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    item["deleted"] = True
    return {"message": "Item deleted"}
