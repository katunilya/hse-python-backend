from fastapi import FastAPI, HTTPException, status, Query, Body, Response, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
import logging
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
logging.basicConfig(level=logging.INFO)

Instrumentator().instrument(app).expose(app)

class ItemCreate(BaseModel):
    name: str
    price: float

    model_config = {
        "extra": "forbid"
    }

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

    model_config = {
        "extra": "forbid"
    }

class Item(BaseModel):
    id: int
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
    items: List[CartItem] = []
    price: float = 0.0
    quantity: int = 0

items_db: Dict[int, Item] = {}
carts_db: Dict[int, Cart] = {}

item_id_counter = 0
cart_id_counter = 0

@app.post("/cart", status_code=status.HTTP_201_CREATED)
def create_cart(response: Response):
    global cart_id_counter
    cart_id_counter += 1
    cart_id = cart_id_counter
    new_cart = Cart(id=cart_id)
    carts_db[cart_id] = new_cart
    response.headers["location"] = f"/cart/{cart_id}"
    logging.info(f"Создана новая корзина: {cart_id}")
    return {"id": cart_id}

@app.get("/cart/{id}")
def get_cart(id: int):
    if id not in carts_db:
        logging.error(f"Корзина с идентификатором {id} не найдена")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Корзина не найдена")
    cart = carts_db[id]
    total_price = 0.0
    total_quantity = 0
    for cart_item in cart.items:
        item = items_db.get(cart_item.id)
        if item:
            cart_item.available = not item.deleted
            cart_item.name = item.name
            total_price += item.price * cart_item.quantity
            total_quantity += cart_item.quantity
        else:
            cart_item.available = False
    cart.price = total_price
    cart.quantity = total_quantity
    logging.info(f"Получена корзина {id} с общей стоимостью {cart.price}")
    return cart

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
    logging.info(f"Отфильтровано {len(filtered_carts)} корзин")
    start = offset
    end = offset + limit
    return filtered_carts[start:end]

@app.post("/cart/{cart_id}/add/{item_id}")
def add_item_to_cart(cart_id: int, item_id: int):
    if cart_id not in carts_db:
        logging.error(f"Корзина с идентификатором {cart_id} не найдена")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Корзина не найдена")
    if item_id not in items_db:
        logging.error(f"Товар с идентификатором {item_id} не найден")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    cart = carts_db[cart_id]
    item = items_db[item_id]
    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            logging.info(f"Увеличено количество товара {item_id} в корзине {cart_id}")
            break
    else:
        cart_item = CartItem(
            id=item_id,
            name=item.name,
            quantity=1,
            available=not item.deleted
        )
        cart.items.append(cart_item)
        logging.info(f"Добавлен товар {item_id} в корзину {cart_id}")
    return {"message": "Товар добавлен в корзину"}

@app.post("/item", status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, response: Response):
    global item_id_counter
    item_id_counter += 1
    item_id = item_id_counter
    new_item = Item(id=item_id, name=item.name, price=item.price, deleted=False)
    items_db[item_id] = new_item
    response.headers["location"] = f"/item/{item_id}"
    logging.info(f"Создан товар {item_id}")
    return new_item.model_dump()

@app.get("/item/{id}")
def get_item(id: int):
    if id not in items_db or items_db[id].deleted:
        logging.error(f"Товар с идентификатором {id} не найден или удален")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    logging.info(f"Получен товар {id}")
    return items_db[id].model_dump()

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
    logging.info(f"Отфильтровано {len(filtered_items)} товаров")
    start = offset
    end = offset + limit
    return [item.model_dump() for item in filtered_items[start:end]]

@app.put("/item/{id}")
def replace_item(id: int, new_item: ItemCreate):
    if id not in items_db:
        logging.error(f"Товар с идентификатором {id} не найден")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    item = items_db[id]
    if item.deleted:
        logging.warning(f"Попытка изменить удаленный товар {id}")
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
    item.name = new_item.name
    item.price = new_item.price
    logging.info(f"Товар {id} обновлен")
    return item

@app.patch("/item/{id}")
def update_item(id: int, item_updates: ItemUpdate = Body(default={})):
    if id not in items_db:
        logging.error(f"Товар с идентификатором {id} не найден")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товар не найден")
    item = items_db[id]
    if item.deleted:
        logging.warning(f"Попытка изменить удаленный товар {id}")
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
    update_data = item_updates.model_dump(exclude_unset=True)
    if "deleted" in update_data:
        logging.warning(f"Попытка изменить поле 'deleted' для товара {id}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Поле 'deleted' нельзя менять")
    if not update_data:
        logging.info(f"Обновления не предоставлены для товара {id}")
        return item
    for key, value in update_data.items():
        setattr(item, key, value)
    logging.info(f"Товар {id} частично обновлен")
    return item

@app.delete("/item/{id}")
def delete_item(id: int):
    if id not in items_db:
        logging.info(f"Товар {id} уже удален")
        return {"message": "Товар уже удален"}
    item = items_db[id]
    if item.deleted:
        logging.info(f"Товар {id} уже удален")
        return {"message": "Товар уже удален"}
    item.deleted = True
    logging.info(f"Товар {id} удален")
    return {"message": "Товар удален"}

class Manager:
    def __init__(self):
        self.rooms: Dict[str, List[WebSocket]] = {}
        self.users: Dict[WebSocket, str] = {}

    async def connect(self, ws: WebSocket, room: str):
        await ws.accept()
        nick = str(uuid.uuid4())[:8]
        self.users[ws] = nick
        if room not in self.rooms:
            self.rooms[room] = []
        self.rooms[room].append(ws)
        logging.info(f"Пользователь {nick} подключен к комнате {room}")

    def disconnect(self, ws: WebSocket, room: str):
        self.rooms[room].remove(ws)
        del self.users[ws]
        if not self.rooms[room]:
            del self.rooms[room]
        logging.info(f"Пользователь отключен от комнаты {room}")

    async def send(self, msg: str, room: str, sender: WebSocket):
        for ws in self.rooms.get(room, []):
            if ws != sender:
                await ws.send_text(msg)
        logging.info(f"Сообщение отправлено в комнату {room}")

manager = Manager()

@app.websocket("/chat/{room}")
async def chat(ws: WebSocket, room: str):
    await manager.connect(ws, room)
    nick = manager.users[ws]
    try:
        while True:
            text = await ws.receive_text()
            msg = f"{nick} :: {text}"
            await manager.send(msg, room, ws)
    except WebSocketDisconnect:
        manager.disconnect(ws, room)
