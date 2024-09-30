from fastapi import FastAPI, HTTPException
from http import HTTPStatus
from starlette.responses import Response
from typing import List, Optional

from .queries import get_cart, create_cart, get_carts, add_item, get_item, get_items, delete_item, add_item_in_cart, change_item, modify_item
from .models import Cart, Item, ItemPut, ItemPatch

app = FastAPI(title="Shop API")


@app.post(
    "/cart",
    responses={
        HTTPStatus.CREATED: {
            "description": "Successfully created new empty cart",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Failed to created new empty cart. Something went wrong",
        },
    },
    status_code=HTTPStatus.CREATED,
    response_model=Cart
)
def create_new_cart(response: Response):
    cart: Cart = create_cart()
    response.headers['location'] = f'/cart/{cart.id}'
    return cart


@app.get(
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
    response_model=Cart
)
def get_cart_by_id(id: int):
    cart = get_cart(id)
    if cart is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")
    return cart


@app.get(
    "/cart",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned list of carts",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return any carts for theese params",
        },
    },
    status_code=HTTPStatus.OK,
    response_model=List[Cart]
)
def get_carts_by_params(
    limit: Optional[int]= 10, 
    offset: Optional[int] = 0, 
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_quantity: Optional[int] = None,
    max_quantity: Optional[int] = None
    ):
    try:
        carts = get_carts(limit=limit, offset=offset, min_price=min_price, max_price=max_price, min_quantity=min_quantity, max_quantity=max_quantity)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=f"{e}")
    if carts is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Carts not found")
    return carts


@app.post(
    "/cart/{cart_id}/add/{item_id}",
    responses={
        HTTPStatus.CREATED: {
            "description": f"Successfully added item in cart",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Failed to add item in cart. Something went wrong",
        },
    },
    status_code=HTTPStatus.CREATED,
    response_model=Cart
)
def add_new_item_in_cart(cart_id: int, item_id: int):
    try:
        cart = add_item_in_cart(cart_id, item_id)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=f"{e}")
    return cart


@app.post(
    "/item",
    responses={
        HTTPStatus.CREATED: {
            "description": "Successfully created new item",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Failed to create new item. Something went wrong",
        },
    },
    status_code=HTTPStatus.CREATED,
    response_model=Item
)
def create_new_item(request: Item, response: Response):
    try:
        item: Item = add_item(request)
        response.headers['location'] = f'/item/{item.id}'
        return item
    except ValueError as ve:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=str(ve))


@app.get(
    "/item/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested item as one was not found",
        },
    },
    status_code=HTTPStatus.OK,
    response_model=Item
)
def get_item_by_id(id: int):
    item = get_item(id)
    if item is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    return item


@app.get(
    "/item",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned list of items",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return any items for theese params",
        },
    },
    status_code=HTTPStatus.OK,
    response_model=List[Item]
)
def get_items_by_params(
    limit: Optional[int]= 10, 
    offset: Optional[int] = 0, 
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    show_deleted: Optional[bool] = False
    ):
    try:
        items = get_items(limit=limit, offset=offset, min_price=min_price, max_price=max_price, show_deleted=show_deleted)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=f"{e}")
    if items is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Items not found")
    return items


@app.put(
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
    response_model=Item
)
def change_item_by_id(id: int, request: ItemPut):
    try:    
        item = change_item(item_id=id, new_item=request)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Item not found")
    return item


@app.patch(
    "/item/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully modified data of item",
        },
        HTTPStatus.NOT_MODIFIED: {
            "description": "Failed to modify data of item",
        },
    },
    status_code=HTTPStatus.OK,
    response_model=Item
)
def modify_item_by_id(id: int, request: ItemPatch):
    try:
        item = modify_item(item_id=id, new_name=request.name, new_price=request.price)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, detail="Item not found")
    return item


@app.delete(
    "/item/{id}",
    responses={
        HTTPStatus.OK: {"description": "Successfully deleted item"},
        HTTPStatus.NOT_FOUND: {"description": "Failed to delete item"},
    },
    status_code=HTTPStatus.OK,
)
def delete_item_by_id(id: int):
    try:
        item = delete_item(id)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    return item