from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Определение модели товара
class Item(BaseModel):
    id: int = 0
    name: str
    price: float
    deleted: bool = False  # Устанавливаем по умолчанию в False, если товар создан
    quantity: Optional[int] = 1  # Необязательное поле для количества товара

# Определение модели корзины
class Cart(BaseModel):
    id: int
    items: List[Item] = []  # Список товаров в корзине
    price: float = 0.0  # Общая сумма заказа

items_db: List[Item] = []  # Список товаров в памяти
carts_db: List[Cart] = []  # Список корзин в памяти

# Создание нового товара
@app.post("/item", response_model=Item,status_code=201)  # POST /item
async def create_item(item: Item):
    item.id = len(items_db) + 1  # Генерация id
    items_db.append(item)  # Добавляем товар в список
    if item.price < 0:
         raise HTTPException(status_code=422, detail="invalid price")

    return item

# Получение товара по id
@app.get("/item/{id}", response_model=Item, status_code=200)
async def get_item(id: int):
    for item in items_db:
        if item.id == id:
            if item.deleted:
                raise HTTPException(status_code=404, detail="Item not found")
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# Получение списка товаров
@app.get("/item", response_model=List[Item])
async def get_items(offset: int = 0, limit: int = 10, min_price: Optional[float] = None,
                    max_price: Optional[float] = None, show_deleted: bool = False):
    if offset < 0:
        raise HTTPException(status_code=422, detail="Offset must be non-negative.")
    if limit <= 0:
        raise HTTPException(status_code=422, detail="Limit must be greater than 0.")
    if min_price is not None and min_price < 0:
        raise HTTPException(status_code=422, detail="min_price должен быть неотрицательным.")
    if max_price is not None and max_price < 0:
        raise HTTPException(status_code=422, detail="max_price должен быть неотрицательным.")
    
    filtered_items = [item for item in items_db if (show_deleted or not item.deleted)]
    
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item.price >= min_price]
    
    if max_price is not None:
        filtered_items = [item for item in filtered_items if item.price <= max_price]
    
    return filtered_items[offset: offset + limit]

# Замена товара по id
@app.put("/item/{id}", response_model=Item)
async def update_item(id: int, new_item: Item):
    if id < 0:
        raise HTTPException(status_code=422, detail= "id must be positive")
    for index, item in enumerate(items_db):
        if item.id == id:
            new_item.id = id
            items_db[index] = new_item
            return new_item
    raise HTTPException(status_code=404, detail="Item not found")

# Частичное обновление товара по id
@app.patch("/item/{id}", response_model=Item, status_code=200)
async def partial_update_item(
    id: int, request: Request, name: Optional[str] = None, price: Optional[float] = None
):
    body = await request.json()

    # Запрещаем изменение поля 'deleted'
    if 'deleted' in body:
        raise HTTPException(status_code=422, detail="Field 'deleted' cannot be modified.")

    allowed_fields = {"name", "price"}
    for field in body.keys():
        if field not in allowed_fields:
            raise HTTPException(status_code=422, detail=f"Field '{field}' is not allowed.")

    for item in items_db:
        if item.id == id:
            if item.deleted:
                raise HTTPException(status_code=304, detail="Item is deleted.")
            if name is not None:
                item.name = name
            if price is not None:
                if price < 0:
                    raise HTTPException(status_code=422, detail="Price must be non-negative.")
                item.price = price
            return item
    raise HTTPException(status_code=404, detail="Item not found")


# Удаление товара по id
@app.delete("/item/{id}",status_code=200)
async def delete_item(id: int):
    for item in items_db:
        if item.id == id:
            item.deleted = True
            return {"message": "Item successfully deleted."}
    raise HTTPException(status_code=404, detail="Item not found.")

# Создание новой корзины
@app.post("/cart", response_model=dict, status_code=200)  # POST /cart
async def create_cart():
    cart_id = len(carts_db) + 1
    new_cart = Cart(id=cart_id)
    carts_db.append(new_cart)
    return JSONResponse(content={"id": cart_id}, headers={"Location": f"/cart/{cart_id}"},status_code=201)

# Получение корзины по id
@app.get("/cart/{id}", response_model=Cart)
async def get_cart(id: int):
    for cart in carts_db:
        if cart.id == id:
            return cart
    raise HTTPException(status_code=404, detail="Cart not found")

# Получение списка корзин с фильтрами
@app.get("/cart", response_model=List[Cart])
async def get_carts(
    offset: int = 0,
    limit: int = 10,
    min_price: Optional[float] = Query(None, ge=0.0, description="Минимальная цена должна быть неотрицательной"),
    max_price: Optional[float] = Query(None, ge=0.0, description="Максимальная цена должна быть неотрицательной"),
    min_quantity: Optional[int] = Query(None, ge=0, description="Минимальное количество должно быть неотрицательным"),
    max_quantity: Optional[int] = Query(None, ge=0, description="Максимальное количество должно быть неотрицательным")
):
    # Проверка на ограничения
    if offset < 0:
        raise HTTPException(status_code=422, detail="Offset must be non-negative.")
    if limit <= 0:
        raise HTTPException(status_code=422, detail="Limit must be greater than 0.")

    filtered_carts = carts_db

    # Применение фильтров по цене
    if min_price is not None:
        filtered_carts = [cart for cart in filtered_carts if sum(item.price for item in cart.items) >= min_price]

    if max_price is not None:
        filtered_carts = [cart for cart in filtered_carts if sum(item.price for item in cart.items) <= max_price]

    # Применение фильтров по количеству товаров
    if min_quantity is not None:
        filtered_carts = [cart for cart in filtered_carts if sum(item.quantity for item in cart.items) >= min_quantity]

    if max_quantity is not None:
        filtered_carts = [cart for cart in filtered_carts if sum(item.quantity for item in cart.items) <= max_quantity]

    # Пагинация по offset и limit
    return filtered_carts[offset: offset + limit]

# Добавление товара в корзину
@app.post("/cart/{cart_id}/add/{item_id}")
async def add_item_to_cart(cart_id: int, item_id: int):
    cart = next((cart for cart in carts_db if cart.id == cart_id), None)
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")

    item = next((item for item in items_db if item.id == item_id and not item.deleted), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found or deleted")

    # Поиск предмета в корзине
    for cart_item in cart.items:
        if cart_item.id == item.id:
            cart_item.quantity += 1  # Увеличиваем количество
            cart.price += item.price  # Обновляем общую цену
            return {"message": "Item quantity increased"}

    # Если предмета нет, добавляем новый с количеством 1
    item.quantity = 1  # Устанавливаем начальное количество 1
    cart.items.append(item)  # Добавляем товар в корзину
    cart.price += item.price  # Обновляем общую цену

    return {"message": "Item added to cart"}
