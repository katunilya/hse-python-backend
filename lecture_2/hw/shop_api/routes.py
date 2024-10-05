from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import NonNegativeInt, PositiveInt, NonNegativeFloat
from lecture_2.hw.shop_api import store
from lecture_2.hw.shop_api.contracts import (
    ItemRequest,
    PatchItemRequest,
    ItemResponse,
    CartResponse,
    CartRequest,
)

router = APIRouter()

objects_mapping = {
    "item": ItemResponse,
    "cart": CartResponse
}


async def post_request(object_type: str, info, response):
    entity = store.add(object_type, info.as_info())
    response.headers["location"] = f"/item/{entity.id}"

    return objects_mapping[object_type].from_entity(entity)


async def get_many_request(object_type: str, constraints, offset, limit, min_price: float = float("-inf"),
                           max_price: float = float("+inf")):
    cur_class = objects_mapping[object_type]

    return [cur_class.from_entity(e) for e in store.get_many(
        object_type,
        constraints,
        offset,
        limit,
        min_price,
        max_price
    )]


@router.post("/item", status_code=HTTPStatus.CREATED)
async def post_item(item: ItemRequest, response: Response) -> ItemResponse:
    return await post_request("item", item, response)


@router.post("/cart", status_code=HTTPStatus.CREATED)
async def post_cart(response: Response) -> CartResponse:
    return await post_request("cart", CartRequest(), response)


@router.post("/cart/{cart_id}/add/{item_id}",
             responses={
                 HTTPStatus.OK: {
                     "description": "Successfully added item to cart",
                 },
                 HTTPStatus.NOT_FOUND: {
                     "description": "Failed to add item to cart",
                 },
             })
async def post_add_item_to_cart(cart_id: int, item_id: int):
    cart_entity = store.get_one("cart", cart_id)
    item_entity = store.get_one("item", item_id)
    if cart_entity is None:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request cart with id: {cart_id} was not found",
        )
    if item_entity is None:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request item with id: {item_id} was not found",
        )
    store.add_to_cart(cart_entity, item_id)
    return Response(status_code=200)


@router.get("/item")
async def get_item_list(
        offset: Annotated[NonNegativeInt, Query()] = 0,
        limit: Annotated[PositiveInt, Query()] = 10,
        min_price: Annotated[NonNegativeFloat, Query()] = 0,
        max_price: Annotated[NonNegativeFloat, Query()] = float("+inf"),
        show_deleted: Annotated[bool, Query()] = False
) -> list[ItemResponse]:
    return await get_many_request("item",
                                  (show_deleted,),
                                  offset,
                                  limit,
                                  min_price,
                                  max_price)


async def get_obj_by_id(object_type: str, id: int):
    entity = store.get_one(object_type, id)

    if not entity:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /item/{id} was not found",
        )

    return objects_mapping[object_type].from_entity(entity)


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
async def get_item_by_id(id: int) -> ItemResponse:
    return await get_obj_by_id("item", id)


@router.get("/cart")
async def get_cart_list(
        offset: Annotated[NonNegativeInt, Query()] = 0,
        limit: Annotated[PositiveInt, Query()] = 10,
        min_price: Annotated[NonNegativeFloat, Query()] = 0,
        max_price: Annotated[NonNegativeFloat, Query()] = float("+inf"),
        min_quantity: Annotated[NonNegativeInt, Query()] = 0,
        max_quantity: Annotated[NonNegativeInt | None, Query()] = None,
) -> list[CartResponse]:
    return await get_many_request(
        "cart",
        (min_quantity, max_quantity),
        offset,
        limit,
        min_price,
        max_price
    )


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
)
async def get_cart_by_id(id: int) -> CartResponse:
    return await get_obj_by_id("cart", id)


@router.put(
    "/item/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully patched item",
        },
        HTTPStatus.NOT_MODIFIED: {
            "description": "Failed to update item as one was not found",
        },
    },
)
async def put_item(id: int, info: ItemRequest) -> ItemResponse:
    entity = store.put(id, info.as_info())

    if entity is None:
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            f"Requested resource /item/{id} was not found",
        )

    return ItemResponse.from_entity(entity)


@router.patch(
    "/item/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully patched item",
        },
        HTTPStatus.NOT_MODIFIED: {
            "description": "Failed to modify item as one was not found",
        },
    },
)
async def patch_item(id: int, info: PatchItemRequest) -> ItemResponse:
    entity = store.patch(id, info.as_patch_item_info())

    if entity is None:
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            f"Requested resource /item/{id} was not found",
        )

    return ItemResponse.from_entity(entity)


@router.delete("/item/{id}")
async def delete_item(id: int) -> Response:
    store.delete(id)
    return Response("")
