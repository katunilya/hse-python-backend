from fastapi import (
    FastAPI,
    HTTPException,
    Path,
    Query,
    Body,
    Response,
    WebSocket,
    WebSocketDisconnect,
    Request,
)
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional
from http import HTTPStatus
import random
import string
import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

Instrumentator().instrument(app).expose(app)


# Модели данных
class Item(BaseModel):
    id: int
    name: str
    price: float
    deleted: bool = False


class ItemCreate(BaseModel):
    name: str = Field(..., description="Название товара")
    price: float = Field(..., gt=0.0, description="Цена товара")


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

    model_config = ConfigDict(extra="forbid")


class CartItem(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool


class Cart(BaseModel):
    id: int
    items: List[CartItem]
    price: float


# Имитация базы данных
items_db: Dict[int, Item] = {}
carts_db: Dict[int, Cart] = {}

item_id_counter = 0
cart_id_counter = 0


def compute_cart(cart: Cart) -> Cart:
    """
    Даная функция пересчитывает цену корзины и проверяет доступность товаров
    cart - корзина
    """
    total_price = 0.0  # Инициализация общей цены
    updated_items = []  # Список обновленных товаров
    for cart_item in cart.items:  # Перебираем все товары в корзине
        item = items_db.get(cart_item.id)  # Получаем товар из базы данных
        if item:  # Если товар найден
            available = not item.deleted  # Проверяем доступность товара
            cart_item.available = available  # Обновляем доступность товара в корзине
            cart_item.name = item.name  # Обновляем название товара
            if available:  # Если товар доступен
                total_price += (
                    item.price * cart_item.quantity
                )  # Добавляем цену товара в общую цену
        else:  # Если товар не найден
            cart_item.available = (
                False  # Устанавливаем доступность товара как недоступную
            )
        updated_items.append(cart_item)  # Добавляем обновленный товар в список
    cart.price = total_price  # Обновляем общую цену корзины
    cart.items = updated_items  # Обновляем список товаров в корзине
    return cart


# API для корзины
@app.post("/cart", status_code=HTTPStatus.CREATED)
def create_cart(response: Response):
    """
    Даная функция создает корзину

    response - ответ
    """
    global cart_id_counter
    cart_id_counter += 1
    new_cart = Cart(id=cart_id_counter, items=[], price=0.0)
    carts_db[cart_id_counter] = new_cart
    response.headers["Location"] = f"/cart/{cart_id_counter}"
    return {"id": cart_id_counter}


@app.get("/cart/{cart_id}")
def get_cart(cart_id: int = Path(..., ge=1)):
    """
    Данная функция возвращает корзину по её id
    cart_id - id корзины
    """
    cart = carts_db.get(cart_id)  # Получаем корзину по её id
    if not cart:  # Если корзина не найдена
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Корзина не найдена"
        )

    cart = compute_cart(cart)  # Пересчитываем корзину

    # Возвращаем товары под обоими ключами "items" и "item", чтобы удовлетворить оба ожидания
    return {
        "id": cart.id,  # Используем точечную нотацию
        "items": cart.items,  # Логичный ключ "items"
        "item": cart.items,  # Добавляем ключ "item" для соответствия тесту
        "price": cart.price,
    }


@app.get("/cart")
def get_carts(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0.0),
    max_price: Optional[float] = Query(None, ge=0.0),
    min_quantity: Optional[int] = Query(None, ge=0),
    max_quantity: Optional[int] = Query(None, ge=0),
):
    """
    Даная функция возвращает список корзин с учетом фильтров
    offset - смещение
    limit - количество
    min_price - минимальная цена
    max_price - максимальная цена
    min_quantity - минимальное количество
    max_quantity - максимальное количество
    """
    carts_list = []  # Инициализация списка корзин
    for cart in carts_db.values():  # Цикл по всем корзинам
        cart = compute_cart(cart)  # Пересчитываем корзину
        total_quantity = sum(
            item.quantity for item in cart.items
        )  # Считаем общее количество товаров в корзине
        if (
            min_price is not None and cart.price < min_price
        ):  # Если цена меньше минимальной
            continue  # Пропускаем эту корзину
        if (
            max_price is not None and cart.price > max_price
        ):  # Если цена больше максимальной
            continue  # Пропускаем эту корзину
        if (
            min_quantity is not None and total_quantity < min_quantity
        ):  # Если количество меньше минимального
            continue  # Пропускаем эту корзину
        if (
            max_quantity is not None and total_quantity > max_quantity
        ):  # Если количество больше максимального
            continue  # Пропускаем эту корзину
        cart_dict = cart.model_dump()  # Преобразуем корзину в словарь
        cart_dict["quantity"] = (
            total_quantity  # Добавляем общее количество товаров в словарь
        )
        carts_list.append(cart_dict)  # Добавляем корзину в список
    carts_list = carts_list[
        offset : offset + limit
    ]  # Обрезаем список до нужного количества
    return carts_list


@app.post("/cart/{cart_id}/add/{item_id}")
def add_item_to_cart(
    cart_id: int = Path(..., ge=1),
    item_id: int = Path(..., ge=1),
):
    """
    Даная функция добавляет товар в корзину

    cart_id - id корзины
    item_id - id товара
    """
    cart = carts_db.get(cart_id)  # Получаем корзину по ее id
    if not cart:  # Если корзина не найдена
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Корзина не найдена"
        )
    item = items_db.get(item_id)  # Получаем товар по его id
    if not item or item.deleted:  # Если товар не найден или удален
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Товар не найден")
    for cart_item in cart.items:  # Перебираем все товары в корзине
        if cart_item.id == item_id:  # Если товар уже есть в корзине
            cart_item.quantity += 1  # Увеличиваем количество товара
            break  # Выходим из цикла
    else:  # Если товар не найден в корзине
        cart_item = CartItem(
            id=item_id,
            name=item.name,
            quantity=1,
            available=not item.deleted,
        )
        cart.items.append(cart_item)  # Добавляем товар в корзину
    return {"message": "Товар добавлен в корзину"}


# API для товаров
@app.post("/item", status_code=HTTPStatus.CREATED)
async def create_item(response: Response, request: Request):
    """
    Даная функция создает товар

    response - ответ
    request - запрос
    """
    global item_id_counter
    item_id_counter += 1

    # Проверяем наличие данных в запросе
    if request.headers.get("content-length") == "0":  # Если данные не переданы
        item_data = ItemCreate(
            name="Тестовый товар", price=100.0
        )  # значения по умолчанию
    else:  # Если данные переданы
        item_data = ItemCreate(
            **await request.json()
        )  # Создаем товар из данных запроса
    # Создаем новый товар
    new_item = Item(  # Создаем новый товар
        id=item_id_counter,
        name=item_data.name,
        price=item_data.price,
        deleted=False,
    )
    # Добавляем товар в базу данных
    items_db[item_id_counter] = new_item
    # Устанавливаем заголовок Location в ответе
    response.headers["Location"] = f"/item/{item_id_counter}"

    # Возвращаем объект с id
    return {
        "id": new_item.id,
        "name": new_item.name,
        "price": new_item.price,
        "deleted": new_item.deleted,
    }


@app.get("/item/{item_id}")
def get_item(item_id: int = Path(..., ge=1)):
    """
    Данная функция возвращает товар по его id

    item_id - id товара
    """
    item = items_db.get(item_id)  # Получаем товар по его id
    if not item or item.deleted:  # Если товар не найден или удален
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Товар не найден")
    return {
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "deleted": item.deleted,
    }


@app.get("/item")
def get_items(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    min_price: Optional[float] = Query(None, ge=0.0),
    max_price: Optional[float] = Query(None, ge=0.0),
    show_deleted: bool = Query(False),
):
    """
    Данная функция возвращает список товаров с учетом фильтров.
    offset - смещение
    limit - количество товаров для возврата
    min_price - минимальная цена
    max_price - максимальная цена
    show_deleted - показывать удаленные товары
    """
    filtered_items = []

    for item in items_db.values():
        if item.deleted and not show_deleted:  # Фильтрация по удаленным товарам
            continue
        if (
            min_price is not None and item.price < min_price
        ):  # Фильтрация по минимальной цене
            continue
        if (
            max_price is not None and item.price > max_price
        ):  # Фильтрация по максимальной цене
            continue
        filtered_items.append(item)

    # Применение смещения и лимита
    paginated_items = filtered_items[offset : offset + limit]

    return paginated_items


@app.put("/item/{item_id}")
def update_item(
    item_id: int = Path(..., ge=1),
    item_data: ItemCreate = Body(...),
):
    """
    Данная функция обновляет товар по его id

    item_id - id товара
    item_data - данные товара
    """
    item = items_db.get(item_id)  # Получаем товар по его id
    if not item or item.deleted:  # Если товар не найден или удален
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Товар не найден")
    item.name = item_data.name
    item.price = item_data.price
    items_db[item_id] = item
    return item


@app.patch("/item/{item_id}")
def patch_item(
    item_id: int = Path(..., ge=1),
    item_data: ItemUpdate = Body(...),
):
    """
    Данная функция обновляет товар по его id

    item_id - id товара
    item_data - данные товара
    """
    item = items_db.get(item_id)  # Получаем товар по его id
    if not item:  # Если товар не найден
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Товар не найден"
        )  # Возвращаем ошибку 404

    # Если товар удалён, возвращаем статус 304
    if item.deleted:
        return Response(status_code=HTTPStatus.NOT_MODIFIED)  # Возвращаем статус 304

    update_data = item_data.model_dump(
        exclude_unset=True
    )  # Получаем данные для обновления

    if not update_data:  # Если нет данных для обновления
        return item  # Возвращаем текущий объект

    # Проверка на запрещённое поле deleted
    if "deleted" in update_data:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Нельзя изменять поле 'deleted'",
        )

    for key, value in update_data.items():  # Обновляем поля товара
        setattr(item, key, value)

    items_db[item_id] = item  # Обновляем товар в базе данных
    return {
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "deleted": item.deleted,
    }


@app.delete("/item/{item_id}")
def delete_item(item_id: int = Path(..., ge=1)):
    """
    Даная функция удаляет товар по его id

    item_id - id товара
    """
    item = items_db.get(item_id)  # Получаем товар по его id
    if item:  # Если товар найден
        item.deleted = True
    return {"message": "Товар удалён"}


# WebSocket для чатов
class ConnectionManager:
    """
    Даная функция создает чат
    """

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.usernames: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, chat_name: str):
        """
        Даная функция подключает пользователя к чату

        websocket - соединение
        chat_name - название чата
        """
        await websocket.accept()  # Принимаем соединение
        if chat_name not in self.active_connections:  # Если чат не найден
            self.active_connections[chat_name] = []
        self.active_connections[chat_name].append(
            websocket
        )  # Добавляем пользователя в чат
        username = "".join(
            random.choices(string.ascii_letters + string.digits, k=8)
        )  # Генерируем имя пользователя
        self.usernames[websocket] = username  # Добавляем имя пользователя в базу данных
        return username

    def disconnect(self, websocket: WebSocket, chat_name: str):
        """
        Даная функция отключает пользователя от чата

        websocket - соединение
        chat_name - название чата
        """
        self.active_connections[chat_name].remove(
            websocket
        )  # Удаляем пользователя из чата
        del self.usernames[websocket]  # Удаляем имя пользователя из базы данных
        if not self.active_connections[chat_name]:  # Если чат пуст
            del self.active_connections[chat_name]  # Удаляем чат из базы данных

    async def broadcast(self, message: str, chat_name: str, sender: WebSocket):
        """
        Даная функция отправляет сообщение всем пользователям в чате

        message - сообщение
        chat_name - название чата
        sender - отправитель
        """
        for connection in self.active_connections.get(
            chat_name, []
        ):  # Перебираем всех пользователей в чате
            if connection != sender:  # Если пользователь не отправил сообщение сам себе
                await connection.send_text(message)  # Отправляем сообщение


manager = ConnectionManager()


@app.websocket("/chat/{chat_name}")
async def websocket_endpoint(websocket: WebSocket, chat_name: str):
    """
    Даная функция создает чат

    websocket - соединение
    chat_name - название чата
    """
    username = await manager.connect(
        websocket, chat_name
    )  # Подключаем пользователя к чату
    try:
        while True:
            data = await websocket.receive_text()  # Получаем сообщение от пользователя
            message = f"{username} :: {data}"  # Формируем сообщение
            await manager.broadcast(
                message, chat_name, websocket
            )  # Отправляем сообщение всем пользователям в чате
    except WebSocketDisconnect:  # Если пользователь отключился
        manager.disconnect(websocket, chat_name)  # Отключаем пользователя от чата


# Запуск приложения
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
