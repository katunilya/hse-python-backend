from typing import Annotated, List

from fastapi import APIRouter, HTTPException, Query, Response
from http import HTTPStatus
from pydantic import NonNegativeInt, PositiveInt, NonNegativeFloat

from lecture_2.hw.shop_api.store import data_carts, data_items, CartItem, cart_id_generator,Cart, item_id_generator,Item
from lecture_2.hw.shop_api.api.contracts import CartResponse, ItemPatchRequest, ItemRequest
router = APIRouter(prefix="")

@router.post(
    "/cart/",
    responses={
        HTTPStatus.CREATED: {
            "description": "Successfully created new empty cart",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Failed to created new empty cart. Something went wrong",
        },
    },
    status_code=HTTPStatus.CREATED,
    response_model=CartResponse,
)
async def post_cart(response: Response) -> CartResponse:
    try:
        cart_id = next(cart_id_generator)
        new_cart = Cart(id=cart_id, items=[], price=0.0)
        data_carts[cart_id] = new_cart
        response.headers["location"] = f"/cart/{new_cart.id}"
        return new_cart
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))


@router.get(
    "/cart/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested cart",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested cart as one was not found",
        },
    },
    status_code=HTTPStatus.OK,
    response_model=CartResponse,
)
async def get_cart_by_id(id: int) -> CartResponse:

    try:
        cart = data_carts.get(id)
        if cart is None:
            raise HTTPException(HTTPStatus.NOT_FOUND,f"Request resource /cart/{id} was not found")
        return cart
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))


@router.get("/cart/")
async def get_сart_list(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: Annotated[NonNegativeInt, Query()] = 0,
    max_price: Annotated[NonNegativeInt, Query()] = 999,
    min_quantity: Annotated[NonNegativeInt, Query()] = 0,
    max_quantity: Annotated[NonNegativeInt, Query()] = 99,
) -> List[CartResponse]:

    try:
        carts_list = []
        curr = 0
        for id, info in data_carts.items():
            if offset <= curr < offset + limit:
                if min_price <= info.price <= max_price:
                    for item in info.items:
                        if min_quantity <= item.quantity <= max_quantity:
                    # yield Cart(id, info)
                            carts_list.append(info)
                            curr += 1
        return carts_list
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))



@router.post(
    "/item/",
    responses={
        HTTPStatus.CREATED: {
            "description": "Successfully created new item",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Failed to create new item. Something went wrong",
        },
    },
    status_code=HTTPStatus.CREATED,
    response_model=Item,
)

async def post_item(item_request: ItemRequest, response: Response) -> Item:
    try:
        item_id = next(item_id_generator)
        new_item = Item(id=item_id, name=item_request.name, price=item_request.price)
        data_items[item_id] = new_item
        response.headers["location"] = f"/item/{new_item.id}"
        return new_item
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))


@router.get(
    "/item/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested item as one was not found",
        },
    },
)
async def get_item_by_id(id: int):# -> ItemResponse:
    item = data_items.get(id)

    if not item or item.deleted:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /item/{id} was not found",
        )

    return {
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "deleted": item.deleted,
    }

@router.get("/item/",
    responses = {
        HTTPStatus.OK: {
            "description": "Successfully returned list of items",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return any items for theese params",
        },
    },
    status_code = HTTPStatus.OK,
    response_model = List[Item],
)
async def get_item_list(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: Annotated[NonNegativeFloat, Query()] = 0,
    max_price: Annotated[NonNegativeFloat, Query()] = 9999,
    show_deleted: Annotated[bool, Query()] = True,

) -> list[Item]:
    try:
        curr = 0
        item_list = []
        items = data_items.items()
        for id, info in items:
            if info.deleted and not show_deleted:
                continue
            if min_price is not None and info.price < min_price:
                continue
            if max_price is not None and info.price > max_price:
                continue
            if offset <= curr < offset + limit:
                curr += 1
                item_list.append(info)

    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))
    if items is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Items not found")
    return item_list

@router.put(
    "/item/{id}",
   responses={
        HTTPStatus.OK: {
            "description": "Successfully changed data of item",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Failed to changed data of item",
        },
    },
    status_code=HTTPStatus.OK,
    response_model=Item,
)
async def put_item(id: int, item_request: ItemRequest) -> Item:

    try:
        item = data_items[id]
        if item is None or item.deleted:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Параметры  указаны неверно")
        item.name = item_request.name
        item.price = item_request.price
        return item
    except:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Параметры  указаны неверно")



@router.patch("/item/{id}")
async def patch_item(id: int, item_patch_request: ItemPatchRequest) -> Item:
    try:
        item = data_items[id]
    except:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Товар не найден")
    if item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, detail="Нет такого товара")

    if item_patch_request.deleted == True:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Нельзя изменять поле")
    if item_patch_request.name != None:
        item.name = item_patch_request.name

    if item_patch_request.price != None:
        item.price = item_patch_request.price
    return item

@router.delete("/item/{id}",
    responses={
        HTTPStatus.OK: {"description": "Successfully deleted item"},
        HTTPStatus.NOT_FOUND: {"description": "Failed to delete item"},
    },
    status_code=HTTPStatus.OK,
)
async def delete_item(id: int) -> Response:
    try:
        item = data_items.get(id)
        item.deleted = True
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e))
    return item

@router.post(
    "/cart/{cart_id}/add/{item_id}",
    responses={
        HTTPStatus.CREATED: {
            "description": "Successfully added item to cart",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Failed to add item to cart. Something went wrong",
        },
    },
    status_code=HTTPStatus.CREATED,
    response_model=CartResponse,
)
async def post_cart_item(cart_id: int, item_id: int) -> CartResponse:
    try:
        cart = data_carts.get(cart_id)
        if not cart:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Корзина не найдена")
        item = data_items.get(item_id)
        if not item or item.deleted:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Товар не найден")

        for cart_item in cart.items:
            if cart_item.id == item_id:
                cart_item.quantity += 1
                break
        else:
            cart.items.append(
                CartItem(id=item.id, name=item.name, quantity=1, available=True)
            )
        cart.price += item.price
        return cart
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(e))

