from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as HTTPStatus
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from typing import Annotated, List, Optional

import lecture_2.hw.shop_api.models as models
import lecture_2.hw.shop_api.schemas as schemas
from lecture_2.hw.shop_api.routers.utils import get_db

__all__ = ["carts_router"]

carts_router = APIRouter(prefix="/cart")


@carts_router.get(
    path="/{id}",
    responses={
        HTTPStatus.HTTP_200_OK: {
            "description": "Successfully received cart",
            "model": schemas.Cart,
        },
        HTTPStatus.HTTP_404_NOT_FOUND: {
            "description": "Failed to receive cart as one was not found",
            "model": schemas.Message,
        },
    },
)
async def get_cart(
    id: int,
    db: Session = Depends(get_db),
) -> schemas.Cart:
    """
    Gets cart by given ID.

    Args:
    id (int):
        Represents ID of the Cart that has to be returned.
    db (Session, optional):
        Represents connection to database.

    Raises:
    HTTPException:
        Represents exception which raises in case Cart with provided ID doesn't exist.

    Returns:
    schemas.Cart:
        Represents Cart which has been requested.
    """
    cart = db.query(models.Cart).filter(models.Cart.id == id).first()
    if not cart:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Cart with ID {id} wasn't found")

    return schemas.Cart.from_cart_model(cart=cart)


@carts_router.get(
    path="/",
    responses={
        HTTPStatus.HTTP_200_OK: {
            "description": "Successfully received carts",
            "model": List[schemas.Cart],
        },
    },
)
async def list_carts(
    db: Session = Depends(get_db),
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0)] = 10,
    min_price: Annotated[Optional[float], Query(ge=0)] = None,
    max_price: Annotated[Optional[float], Query(ge=0)] = None,
    min_quantity: Annotated[Optional[int], Query(ge=0)] = None,
    max_quantity: Annotated[Optional[int], Query(ge=0)] = None,
) -> List[schemas.Cart]:
    """
    Gets list of carts using provided query parameters.

    Args:
    db (Session, optional):
        Represents connection to database.
    offset (Annotated[int, Query, optional):
        Represents count of carts which have to be skipped.
    limit (Annotated[int, Query, optional):
        Represents maximum count of carts which will be returned.
    min_price (Annotated[Optional[float], Query, optional):
        Represents minimum price of the carts which have to be returned.
    max_price (Annotated[Optional[float], Query, optional):
        Represents maximum price of the carts which have to be returned.
    min_quantity (Annotated[Optional[int], Query, optional):
        Represents minimum quantity of items in cart which has to be returned.
    max_quantity (Annotated[Optional[int], Query, optional):
        Represents maximum quantity of items in cart which has to be returned.

    Returns:
    List[schemas.Cart]:
        Represents list of carts which were found using provided search parameters.
    """
    query = db.query(models.Cart)
    if min_price is not None:
        query = query.filter(models.Cart.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Cart.price <= max_price)
    if min_quantity is not None:
        query = query.filter(models.Cart.quantity >= min_quantity)
    if max_quantity is not None:
        query = query.filter(models.Cart.quantity <= max_quantity)

    carts = query.offset(offset).limit(limit).all()

    schema_carts = []
    for cart in carts:
        schema_carts.append(schemas.Cart.from_cart_model(cart=cart))

    return schema_carts


@carts_router.post(
    path="/",
    status_code=HTTPStatus.HTTP_201_CREATED,
    responses={
        HTTPStatus.HTTP_201_CREATED: {
            "description": "Successfully created cart",
            "model": schemas.Cart,
        },
    },
)
async def create_cart(
    db: Session = Depends(get_db),
) -> schemas.Cart:
    """
    Creates cart with autoincremented ID.

    Args:
    db (Session, optional):
        Represents connection to database.

    Returns:
    schemas.Cart:
        Represents empty cart with new ID.
    """
    id = db.query(func.max(models.Cart.id)).first()[0]
    if not id:
        id = 0
    id += 1

    cart = models.Cart(id=id)

    db.add(cart)
    db.commit()

    return JSONResponse(
        content=jsonable_encoder(schemas.Cart.from_cart_model(cart=cart)),
        headers={"location": f"/cart/{id}"},
        status_code=HTTPStatus.HTTP_201_CREATED,
    )


@carts_router.post(
    path="/{cart_id}/add/{item_id}",
    responses={
        HTTPStatus.HTTP_200_OK: {
            "description": "Successfully received cart",
            "model": schemas.Cart,
        },
        HTTPStatus.HTTP_404_NOT_FOUND: {
            "description": "Failed to receive cart or item as one was not found",
            "model": schemas.Message,
        },
    },
)
async def add_item_to_cart(
    cart_id: int,
    item_id: int,
    db: Session = Depends(get_db),
) -> schemas.Cart:
    """
    Adds item with `item_id` into `cart_id` cart.

    Args:
    cart_id (int):
        Represents ID of cart in which has to be added an item.
    item_id (int):
        Represents ID of item which has to be added in cart.
    db (Session, optional):
        _description_. Defaults to Depends(get_db).

    Raises:
    HTTPException:
        _description_
    HTTPException:
        _description_

    Returns:
    schemas.Cart:
        _description_
    """
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Cart with ID {id} wasn't found")

    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Cart with ID {id} wasn't found")

    for cart_item in cart.items:
        if cart_item.item_id == item.id:
            # Update cart items
            cart_item.quantity += 1
            cart_item.available = not item.deleted
            # Update cart itself
            cart.quantity += 1
            cart.price += item.price
            db.commit()
            db.refresh(cart)

            return schemas.Cart.from_cart_model(cart=cart)

    cart.items.append(models.CartItem(item_id=item.id, quantity=1, cart_id=cart.id))
    cart.quantity += 1
    cart.price += item.price
    db.commit()
    db.refresh(cart)

    return schemas.Cart.from_cart_model(cart=cart)
