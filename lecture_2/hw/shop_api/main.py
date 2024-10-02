from fastapi import FastAPI, HTTPException, status, Query, Body, Response
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

app = FastAPI()

# Модели данных
class ItemCreate(BaseModel):
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
    id: int  # идентификатор товара
    name: str  # название товара
    quantity: int  # количество товара в корзине
    available: bool  # доступен ли товар

class Cart(BaseModel):
    id: int  # идентификатор корзины
    items: List[CartItem] = []  # список товаров в корзине
    price: float = 0.0  # общая сумма заказа
    quantity: int = 0  # общее количество товаров в корзине

# Имитированные "базы данных"
items_db: Dict[int, Item] = {}
carts_db: Dict[int, Cart] = {}

# Счетчики для генерации уникальных идентификаторов
item_id_counter = 0
cart_id_counter = 0

# Создание новой корзины
@app.post("/cart", status_code=status.HTTP_201_CREATED)
def create_cart(response: Response):
    global cart_id_counter
    cart_id_counter += 1
    cart_id = cart_id_counter
    new_cart = Cart(id=cart_id)
    carts_db[cart_id] = new_cart
    response.headers["location"] = f"/cart/{cart_id}"
    return {"id": cart_id}

# Получение корзины по идентификатору
@app.get("/cart/{id}")
def get_cart(id: int):
    if id not in carts_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Корзина не найдена")
    cart = carts_db[id]
    total_price = 0.0
    total_quantity = 0
    for cart_item in cart.items:
        item = items_db.get(cart_item.id)
        if item:
            cart_item.available = not item.deleted
            cart_item.name = item.name  # Обновляем название товара
            total_price += item.price * cart_item.quantity
            total_quantity += cart_item.quantity
        else:
            cart_item.available = False  # Товар не найден
    cart.price = total_price
    cart.quantity = total_quantity
    return cart

# Получение списка корзин с фильтрами
@app.get("/cart")
def list_carts(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0.0),
    max_price: Optional[float] = Query(None, ge=0.0),
    min_quantity: Optional[int] = Query(None, ge=0),
    max_quantity: Optional[int] = Query(None, ge=0),
):
    carts = list(carts_db.values())
    filtered_carts = []
    for cart in carts:
        total_price = 0.0
        total_quantity = 0
        for cart_item in cart.items:
            item = items_db.get(cart_item.id)
            if item and not item.deleted:
                total_price += item.price * cart_item.quantity
                total_quantity += cart_item.quantity
        cart.price = total_price
        cart.quantity = total_quantity
        if min_price is not None and total_price < min_price:
            continue
        if max_price is not None and total_price > max_price:
            continue
        if min_quantity is not None and total_quantity < min_quantity:
            continue
        if max_quantity is not None and total_quantity > max_quantity:
            continue
        filtered_carts.append(cart)
    start = offset
    end = offset + limit
    return filtered_carts[start:end]

# Добавление товара в корзину
@app.post("/cart/{cart_id}/add/{item_id}")
def add_item_to_cart(cart_id: int, item_id: int):
    if cart_id not in carts_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Корзина не найдена")
    if item_id not in items_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    cart = carts_db[cart_id]
    item = items_db[item_id]
    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            break
    else:
        cart_item = CartItem(
            id=item_id,
            name=item.name,
            quantity=1,
            available=not item.deleted
        )
        cart.items.append(cart_item)
    return {"message": "Товар добавлен в корзину"}

# Добавление нового товара
@app.post("/item", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, response: Response):
    global item_id_counter
    item_id_counter += 1
    item_id = item_id_counter
    new_item = Item(id=item_id, name=item.name, price=item.price, deleted=False)
    items_db[item_id] = new_item
    response.headers["location"] = f"/item/{item_id}"
    return new_item

# Получение товара по идентификатору
@app.get("/item/{id}")
def get_item(id: int):
    if id not in items_db or items_db[id].deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    return items_db[id]

# Получение списка товаров с фильтрами
@app.get("/item")
def list_items(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0.0),
    max_price: Optional[float] = Query(None, ge=0.0),
    show_deleted: bool = Query(False),
):
    items = list(items_db.values())
    filtered_items = []
    for item in items:
        if not show_deleted and item.deleted:
            continue
        if min_price is not None and item.price < min_price:
            continue
        if max_price is not None and item.price > max_price:
            continue
        filtered_items.append(item)
    start = offset
    end = offset + limit
    return filtered_items[start:end]

# Замена товара по идентификатору
@app.put("/item/{id}")
def replace_item(id: int, new_item: ItemCreate):
    if id not in items_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    item = items_db[id]
    if item.deleted:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
    item.name = new_item.name
    item.price = new_item.price
    return item

# Частичное обновление товара по идентификатору
@app.patch("/item/{id}")
def update_item(id: int, item_updates: ItemUpdate = Body(default={})):
    if id not in items_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    item = items_db[id]
    if item.deleted:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
    update_data = item_updates.dict(exclude_unset=True)
    if "deleted" in update_data:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Поле 'deleted' нельзя менять")
    if not update_data:
        return item  # No updates provided, return the item as is
    for key, value in update_data.items():
        setattr(item, key, value)
    return item

# Удаление товара по идентификатору
@app.delete("/item/{id}")
def delete_item(id: int):
    if id not in items_db:
        return {"message": "Товар уже удален"}
    item = items_db[id]
    if item.deleted:
        return {"message": "Товар уже удален"}
    item.deleted = True
    return {"message": "Товар удален"}
