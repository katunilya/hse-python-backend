from fastapi import APIRouter, Query
from repository import carts_db, items_db, last_cart_id
from schemas import Cart, CartItem
from typing import Optional, List

router = APIRouter(prefix="/cart")


@router.post("/")
async def create_cart() -> Cart:
    global last_cart_id
    last_cart_id += 1
    carts_db[last_cart_id] = Cart(id=last_cart_id, items=[])
    return carts_db[last_cart_id]


@router.get("/{cart_id}")
async def get_cart(cart_id: int) -> Cart:
    price = get_price_cart(cart_id)
    items = get_cart_items(cart_id, need_all=True)
    return Cart(id=cart_id, items=items, price=price)


def get_cart_items(cart_id: int, need_all: bool = False) -> List[CartItem]:
    item_list = []
    for item in carts_db[cart_id].items:
        if items_db[item.id].deleted:
            item.available = False
        if not items_db[item.id].deleted and not need_all:
            item_list.append(item)
        elif need_all:
            item_list.append(item)
    return item_list


def get_quantity_cart(cart_id: int) -> int:
    quantity = 0
    items = get_cart_items(cart_id)
    for item in items:
        quantity += item.quantity
    return quantity


def get_price_cart(cart_id: int) -> float:
    price = 0
    items = get_cart_items(cart_id)
    for item in items:
        price += items_db[item.id].price * item.quantity
    return price


@router.post("/cart/{cart_id}/add/{item_id}")
async def post_cart_and_item(cart_id: int, item_id: int) -> Cart:
    cart = carts_db[cart_id]
    item = items_db[item_id]

    items_ids = [it.id for it in get_cart_items(cart_id, need_all=True)]
    if item_id not in items_ids:
        cart.items.append(CartItem(id=item_id, name=item.name, quantity=1, available=not item.deleted))
    elif item_id in items_ids:
        cart.items[items_ids.index(item_id)].quantity += 1

    price = get_price_cart(cart_id)
    return Cart(id=cart_id, items=get_cart_items(cart_id), price=price)


# GET /cart - получение списка корзин с query-параметрами
# offset - неотрицательное целое число, смещение по списку (опционально, по-умолчанию 0)
# limit - положительное целое число, ограничение на количество (опционально, по-умолчанию 10)
# min_price - число с плавающей запятой, минимальная цена включительно (опционально, если нет, не учитывает в фильтре)
# max_price - число с плавающей запятой, максимальная цена включительно (опционально, если нет, не учитывает в фильтре)
# min_quantity - неотрицательное целое число, минимальное общее число товаров включительно (опционально, если нет, не учитывается в фильтре)
# max_quantity - неотрицательное целое число, максимальное общее число товаров включительно (опционально, если нет, не учитывается в фильтре)

@router.get("/")
async def get_carts(offset: int = Query(0, ge=0),
                    limit: int = Query(10, gt=0),
                    min_price: Optional[float] = Query(None, gt=0),
                    max_price: Optional[float] = Query(None, gt=0),
                    min_quantity: Optional[int] = Query(None, gt=0),
                    max_quantity: Optional[int] = Query(None, gt=0),
                    ):
    filtered_carts: List[Cart] = list(filter(lambda cart: (
            (min_price is None or get_price_cart(cart.id) >= min_price) and
            (max_price is None or get_price_cart(cart.id) <= max_price) and
            (min_quantity is None or get_quantity_cart(cart.id) >= min_quantity) and
            (max_quantity is None or get_quantity_cart(cart.id) <= max_quantity)
    ), carts_db.values()))
    filtered_carts = filtered_carts[offset:offset + limit]

    processed_carts = []
    for cart in filtered_carts:
        price = get_price_cart(cart.id)
        items = get_cart_items(cart.id, need_all=True)
        processed_carts.append(Cart(id=cart.id, items=items, price=price))
    return processed_carts
