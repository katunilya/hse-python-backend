from fastapi import APIRouter, Query, Response, HTTPException
from ..repository import carts_db, items_db, last_cart_id
from ..schemas import Cart, CartItem
from typing import Optional, List
import http

router = APIRouter(prefix="/cart")


@router.post("/", status_code=http.HTTPStatus.CREATED)
async def create_cart(response: Response) -> Cart:
    global last_cart_id
    last_cart_id += 1
    carts_db[last_cart_id] = Cart(id=last_cart_id, items=[])
    response.headers["Location"] = f"/cart/{last_cart_id}"
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
        if not items_db[item.id].deleted:
            item_list.append(item)
        elif need_all:
            item_list.append(item)
    return item_list


def get_quantity_cart(cart_id: int) -> int:
    quantity = 0
    items = get_cart_items(cart_id) # допустим need_all=True
    for item in items:
        quantity += item.quantity
    return quantity


def get_price_cart(cart_id: int) -> float:
    price = 0
    items = get_cart_items(cart_id) # допустим need_all=True
    for item in items:
        price += items_db[item.id].price * item.quantity
    return price


@router.post("/{cart_id}/add/{item_id}")
async def post_cart_and_item(cart_id: int, item_id: int) -> Cart:
    item = items_db.get(item_id)
    cart = carts_db.get(cart_id)
    if (item is None or item.deleted is True) or (cart is None):
        raise HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="Item not found")

    items_ids = [it.id for it in get_cart_items(cart_id, need_all=True)]
    if item_id not in items_ids:
        cart.items.append(CartItem(id=item_id, name=item.name, quantity=1, available=not item.deleted))
    elif item_id in items_ids:
        cart.items[items_ids.index(item_id)].quantity += 1

    price = get_price_cart(cart_id)
    items = get_cart_items(cart_id, need_all=True)
    print(items)
    return Cart(id=cart_id, items=items, price=price)

@router.get("/")
async def get_carts(offset: int = Query(0, ge=0),
                    limit: int = Query(10, gt=0),
                    min_price: Optional[float] = Query(None, gt=0),
                    max_price: Optional[float] = Query(None, gt=0),
                    min_quantity: Optional[int] = Query(None, gt=0),
                    max_quantity: Optional[int] = Query(None, ge=0),
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
