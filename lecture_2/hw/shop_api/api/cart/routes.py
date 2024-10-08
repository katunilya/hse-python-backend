from fastapi import APIRouter, HTTPException, Response, Query
from http import HTTPStatus
from typing import List, Optional
from ...store import queries
from ..cart.contracts import CartResponse

router = APIRouter(prefix="/cart")

# Создание новой корзины
@router.post("/", status_code=HTTPStatus.CREATED, response_model=CartResponse)
async def create_cart(response: Response):
    cart = queries.create_cart()
    response.headers["location"] = f"/cart/{cart['id']}"
    return cart

# Получение списка корзин с фильтрацией и пагинацией
@router.get("/", response_model=List[CartResponse], status_code=HTTPStatus.OK)
async def get_cart_list(
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, gt=0)
):
    # Проверяем пагинацию
    if offset < 0 or limit <= 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid pagination parameters")

    # Получаем корзины через функцию queries
    filtered_carts = queries.get_carts(offset, limit, min_price, max_price, None, None)

    if not filtered_carts:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Carts not found")

    return filtered_carts

# Добавление товара в корзину
@router.post("/{cart_id}/add/{item_id}", response_model=CartResponse, status_code=HTTPStatus.CREATED)
async def add_item_to_cart(cart_id: int, item_id: int):
    result = queries.add_item(cart_id, item_id)
    if not result:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item or Cart not found")
    return result