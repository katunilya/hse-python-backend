from typing import List, Annotated

from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import PositiveFloat, NonNegativeInt, PositiveInt, NonNegativeFloat

from .schemas import (
    CartResponse,
    ItemRequest,
    ItemResponse,
    PatchItemRequest,
)
from .. import shop

cart_router = APIRouter(prefix="/cart")
item_router = APIRouter(prefix="/item")


# def create_cart_via_grpc():
#     with grpc.insecure_channel("localhost:50051") as channel:
#         stub = cart_pb2_grpc.CartServiceStub(channel)
#         response = stub.CreateCart(cart_pb2.CreateCartRequest())
#         return response.cart_id


@cart_router.post(
    "/",
    responses={
        HTTPStatus.CREATED: {
            "description": "Successfully created new cart",
        }
    },
    status_code=HTTPStatus.CREATED,
)
def create_cart(response: Response):
    # try:
    #     new_cart_id = create_cart_via_grpc()
    #     return new_cart_id

    # except grpc.RpcError as e:
    #     raise HTTPException(status_code=500, detail=str(e)) from e

    _id, cart = shop.post_cart()
    response.headers["location"] = f"/cart/{_id}"

    return CartResponse.from_entity(cart)


@cart_router.get("/")
def get_carts(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: Annotated[NonNegativeFloat, Query()] = 0,
    max_price: Annotated[PositiveFloat, Query()] = None,
    min_quantity: Annotated[NonNegativeInt, Query()] = 0,
    max_quantity: Annotated[NonNegativeInt, Query()] = None,
) -> List[CartResponse]:
    cart_list = shop.get_carts(
        offset=offset,
        limit=limit,
        min_price=min_price,
        max_price=max_price,
        min_quantity=min_quantity,
        max_quantity=max_quantity,
    )

    return [CartResponse.from_entity(e) for e in cart_list]


@cart_router.get(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested cart",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Cart doesn't exist",
        },
    },
)
async def get_cart_by_id(id: int) -> CartResponse:
    cart = shop.get_cart(id)

    if cart is None:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /cart/{id} was not found",
        )

    return CartResponse.from_entity(cart)


@cart_router.get(
    "/{cart_id}/add/{item_id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully added item to cart",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Cart or item doesn't exist",
        },
    },
)
async def add_item_to_cart(cart_id: int, item_id: int) -> CartResponse:
    cart, item = shop.add_item_to_cart(cart_id, item_id)

    if cart is None:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Cart {cart_id} was not found",
        )

    if item is None:
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            f"Item {item_id} was not found",
        )

    return CartResponse.from_entity(cart)


@item_router.post(
    "/",
    responses={
        HTTPStatus.CREATED: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Item doesn't exist",
        },
    },
    status_code=HTTPStatus.CREATED,
)
def post_item(info: ItemRequest, response: Response) -> ItemResponse:
    item = shop.add_item(info=info)
    response.headers["location"] = f"/item/{item.id}"

    return ItemResponse.from_entity(item)


@item_router.get(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Item doesn't exist",
        },
    },
)
def get_item(id: int):
    item = shop.get_item(id)

    if item is None or item.info.deleted:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Item {id} was not found",
        )

    return ItemResponse.from_entity(item)


@item_router.get("/")
def get_items(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: Annotated[NonNegativeFloat, Query()] = 0,
    max_price: Annotated[PositiveFloat, Query()] = None,
) -> List[ItemResponse]:
    item_list = shop.get_items(
        offset=offset,
        limit=limit,
        min_price=min_price,
        max_price=max_price,
    )

    return [ItemResponse.from_entity(e) for e in item_list]


@item_router.put(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Item doesn't exist",
        },
    },
)
def put_item(id: int, info: ItemRequest) -> ItemResponse:
    item = shop.update_item(id, info.as_item_info())

    if item is None:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Item {id} was not found",
        )

    return ItemResponse.from_entity(item)


@item_router.patch(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Item doesn't exist",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Cannot patch field deleted",
        },
        HTTPStatus.NOT_MODIFIED: {
            "description": "Not modified",
        },
    },
)
def patch_item(id: int, info: PatchItemRequest) -> ItemResponse:
    orig_item = shop.get_item(id)

    if orig_item is None:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Item {id} was not found",
        )
    
    orig_info = orig_item.info
    o_name, o_price, o_deleted = orig_info.name, orig_info.price, orig_info.deleted
    info = info.as_patch_item_info()

    
    if o_deleted:
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            "Item was not modified",
        )

    item = shop.patch_item(id, info)

    if (o_name == item.info.name and o_price == item.info.price) or (
        info.price is None and info.name is None
    ):
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            "Item was not modified",
        )

    return ItemResponse.from_entity(item)


@item_router.delete(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Item doesn't exist",
        },
    },
)
def delete_item(id: int) -> ItemResponse:
    item = shop.delete_item(id)

    if item is None:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Item {id} was not found",
        )

    return ItemResponse.from_entity(item)
