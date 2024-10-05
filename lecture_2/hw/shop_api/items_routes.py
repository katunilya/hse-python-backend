from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import NonNegativeInt, PositiveInt, NonNegativeFloat

from lecture_2.hw.shop_api.contracts import (
    ItemRequest,
    ItemResponse,
    PatchItemRequest,
    PutItemRequest,
)
from lecture_2.hw.shop_api.models import ItemInfo, Item, PatchItemInfo, ItemInCart, Cart
import lecture_2.hw.shop_api.items_queries as queries


router = APIRouter(prefix="/item")


@router.post("/", status_code=HTTPStatus.CREATED)
async def post_item(request: ItemRequest, response: Response) -> ItemResponse:
    item = queries.add_item(request.to_item_info())

    # as REST states one should provide uri to newly created resource in location header
    response.headers["location"] = f"/item/{item.id}"
    return ItemResponse.from_item(item)


@router.get("/{item_id}", status_code=HTTPStatus.OK)
async def get_item_by_id(item_id: int) -> ItemResponse:
    item = queries.get_item_by_id(item_id)

    if not item:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f"Request resource /items/{item_id} was not found",
        )

    return ItemResponse.from_item(item)


@router.get("/", status_code=HTTPStatus.OK)
async def get_items_list(
    offset: Annotated[NonNegativeInt, Query(ge=0)] = 0,
    limit: Annotated[PositiveInt, Query(gt=0)] = 10,
    min_price: Annotated[NonNegativeFloat | None, Query(ge=0.0)] = None,
    max_price: Annotated[NonNegativeFloat | None, Query(ge=0.0)] = None,
    show_deleted: Annotated[bool, Query()] = False,
) -> list[ItemResponse]:
    if offset < 0 or limit < 0:
        raise HTTPException(
            HTTPStatus.UNPROCESSABLE_ENTITY, "Get parameters must be non-negatitve"
        )
    if (
        min_price is not None
        and min_price < 0
        or max_price is not None
        and max_price < 0
    ):
        raise HTTPException(
            HTTPStatus.UNPROCESSABLE_ENTITY, "Get parameters must be non-negatitve"
        )
    return [
        ItemResponse.from_item(item)
        for item in queries.get_many_items(
            offset, limit, min_price, max_price, show_deleted
        )
    ]


@router.put("/{item_id}", status_code=HTTPStatus.OK)
async def put_item(item_id: int, request: PutItemRequest) -> ItemResponse:
    item = queries.put_item(item_id, request.to_item_info())
    if not item:
        raise HTTPException(
            HTTPStatus.NOT_FOUND, f"Request resource /items/{item_id} was not found"
        )

    return ItemResponse.from_item(item)


@router.patch("/{item_id}", status_code=HTTPStatus.OK)
async def patch_item(item_id: int, request: PatchItemRequest) -> ItemResponse:
    item = queries.patch_item(item_id, request.to_item_info())
    if item == "deleted":
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            f"Request resource /items/{item_id} was not modified",
        )
    elif not item:
        raise HTTPException(
            HTTPStatus.NOT_FOUND, f"Request resource /items/{item_id} was not found"
        )

    return ItemResponse.from_item(item)


@router.delete("/{item_id}", status_code=HTTPStatus.OK)
async def delete_item(item_id: int) -> Response:
    delete_response = queries.delete_item(item_id)
    if delete_response == "deleted" or delete_response == "already deleted":
        return Response(
            status_code=HTTPStatus.OK,
            content=f"Request resource /items/{item_id} was deleted successfully",
        )
    elif delete_response == "not found":
        return Response(
            status_code=HTTPStatus.NOT_FOUND,
            content=f"Request resource /items/{item_id} was not found",
        )
