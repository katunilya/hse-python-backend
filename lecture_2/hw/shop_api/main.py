from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Shop API")

# Модели данных
class Item(BaseModel):
    id: Optional[int] = None  
    name: str
    price: float
    deleted: bool = False

class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool

class Cart(BaseModel):
    id: int
    items: List[CartItem]
    price: float

# In-memory хранилище
items_db = {}
carts_db = {}
cart_id_counter = 1
item_id_counter = 1

# Создание корзины
@app.post("/cart", response_model=Cart, status_code=201)
def create_cart(response: Response):
    global cart_id_counter
    cart = Cart(id=cart_id_counter, items=[], price=0)
    carts_db[cart_id_counter] = cart
    cart_id_counter += 1
    response.headers["location"] = f"/cart/{cart.id}"
    return cart

# Получение корзины по id
@app.get("/cart/{id}", response_model=Cart)
def get_cart(id: int):
    if id not in carts_db:
        raise HTTPException(status_code=404, detail="Cart not found")
    return carts_db[id]

# Добавление предмета в корзину
@app.post("/cart/{cart_id}/add/{item_id}")
def add_item_to_cart(cart_id: int, item_id: int):
    if cart_id not in carts_db:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    if item_id not in items_db or items_db[item_id].deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    
    cart = carts_db[cart_id]
    item = items_db[item_id]
    
    # Добавляем товар в корзину
    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            cart.price += item.price
            return {"message": "Item quantity updated in cart"}
    
    cart.items.append(CartItem(id=item.id, name=item.name, quantity=1, available=True))
    cart.price += item.price
    return {"message": "Item added to cart"}

# Добавление нового товара
@app.post("/item", response_model=Item, status_code=201)
def add_item(item: Item, response: Response):
    global item_id_counter
    item.id = item_id_counter  
    items_db[item_id_counter] = item
    item_id_counter += 1
    response.headers["location"] = f"/item/{item.id}"
    return item

# Получение товара по id
@app.get("/item/{id}", response_model=Item)
def get_item(id: int):
    if id not in items_db or items_db[id].deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[id]

# Удаление товара
@app.delete("/item/{id}", status_code=200)
def delete_item(id: int):
    if id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    items_db[id].deleted = True
    return {"message": "Item deleted"}

# Обновление товара (PUT)
@app.put("/item/{id}", response_model=Item)
def update_item(id: int, updated_item: Item):
    if id not in items_db or items_db[id].deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if updated_item.deleted:
        raise HTTPException(status_code=422, detail="Cannot modify deleted status directly")
    
    existing_item = items_db[id]
    existing_item.name = updated_item.name
    existing_item.price = updated_item.price
    
    return existing_item

from pydantic import ValidationError

# Частичное обновление товара (PATCH)
@app.patch("/item/{id}", response_model=Item)
def patch_item(id: int, updated_fields: dict):
    if id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")

    item = items_db[id]

    if item.deleted:
        raise HTTPException(status_code=304, detail="Item is deleted and cannot be modified")

    if "deleted" in updated_fields:
        raise HTTPException(status_code=422, detail="Cannot modify deleted status directly")

    valid_fields = {"name", "price"}
    for field in updated_fields:
        if field not in valid_fields:
            raise HTTPException(status_code=422, detail=f"Invalid field: {field}")

    if "name" in updated_fields:
        item.name = updated_fields["name"]
    if "price" in updated_fields:
        item.price = updated_fields["price"]

    return item



# Список корзин с фильтрацией и пагинацией
@app.get("/cart", response_model=List[Cart])
def get_cart_list(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: float = Query(None, ge=0),
    max_price: float = Query(None, ge=0),
    min_quantity: int = Query(None, ge=0),
    max_quantity: int = Query(None, ge=0),
):
    result = list(carts_db.values())[offset:offset + limit]
    
    if min_price is not None:
        result = [cart for cart in result if cart.price >= min_price]
    if max_price is not None:
        result = [cart for cart in result if cart.price <= max_price]
    if min_quantity is not None:
        result = [cart for cart in result if sum(item.quantity for item in cart.items) >= min_quantity]
    if max_quantity is not None:
        result = [cart for cart in result if sum(item.quantity for item in cart.items) <= max_quantity]
    
    return result

# Список товаров с фильтрацией и пагинацией
@app.get("/item", response_model=List[Item])
def get_item_list(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: float = Query(None, ge=0),
    max_price: float = Query(None, ge=0),
    show_deleted: bool = Query(False)
):
    items = list(items_db.values())[offset:offset + limit]
    
    if min_price is not None:
        items = [item for item in items if item.price >= min_price]
    if max_price is not None:
        items = [item for item in items if item.price <= max_price]
    
    if not show_deleted:
        items = [item for item in items if not item.deleted]
    
    return items
