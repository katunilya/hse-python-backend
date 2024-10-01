from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as HTTPStatus
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from typing import Annotated, List, Optional

import lecture_2.hw.shop_api.models as models
import lecture_2.hw.shop_api.schemas as schemas
from lecture_2.hw.shop_api.routers.utils import get_db

__all__ = ["items_router"]

items_router = APIRouter(prefix="/item")


@items_router.get(
    path="/{id}",
    responses={
        HTTPStatus.HTTP_200_OK: {
            "description": "Successfully received item",
            "model": schemas.Item,
        },
        HTTPStatus.HTTP_404_NOT_FOUND: {
            "description": "Failed to receive item as one was not found",
            "model": schemas.Message,
        },
    },
)
async def get_item(
    id: int,
    db: Session = Depends(get_db),
) -> schemas.Item:
    """
    Gets item by given ID.

    Args:
    id (int):
        Represents ID of the Item that has to be returned.
    db (Session, optional):
        Represents connection to database.

    Raises:
    HTTPException:
        Represents exception which raises in case Item with provided ID doesn't exist.

    Returns:
    schemas.Item:
        Represents Item which has been requested.
    """
    item = db.query(models.Item).filter(models.Item.id == id).first()
    if not item:
        raise HTTPException(status_code=HTTPStatus.HTTP_404_NOT_FOUND, detail=f"Item with ID {id} wasn't found")
    if item.deleted:
        raise HTTPException(status_code=HTTPStatus.HTTP_404_NOT_FOUND, detail=f"Item with ID {id} wasn't found")

    return item


@items_router.get(
    path="/",
    responses={
        HTTPStatus.HTTP_200_OK: {
            "description": "Successfully received items",
            "model": List[schemas.Item],
        },
    },
)
async def list_items(
    db: Session = Depends(get_db),
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0)] = 10,
    min_price: Annotated[Optional[float], Query(ge=0)] = None,
    max_price: Annotated[Optional[float], Query(ge=0)] = None,
    show_deleted: bool = False,
) -> List[schemas.Item]:
    """
    Gets list of items using provided query parameters.

    Args:
    db (Session, optional):
        Represents connection to database.
    offset (Annotated[int, Query, optional):
        Represents count of items which have to be skipped.
    limit (Annotated[int, Query, optional):
        Represents maximum count of items which will be returned.
    min_price (Annotated[Optional[float], Query, optional):
        Represents minimum price of the item which has to be returned.
    max_price (Annotated[Optional[float], Query, optional):
        Represents maximum price of the item which has to be returned.
    show_deleted (bool, optional):
        Represents parameter for returning deleted items.

    Returns:
    List[schemas.Item]:
        Represents list of items which were found using provided search parameters.
    """
    query = db.query(models.Item)
    if min_price is not None:
        query = query.filter(models.Item.price > min_price)
    if max_price is not None:
        query = query.filter(models.Item.price < max_price)
    if show_deleted is False:
        query = query.filter(models.Item.deleted is False)

    items = query.offset(offset).limit(limit).all()

    return items


@items_router.post(
    path="/",
    status_code=HTTPStatus.HTTP_201_CREATED,
    responses={
        HTTPStatus.HTTP_201_CREATED: {
            "description": "Successfully created item",
            "model": schemas.Item,
        },
        HTTPStatus.HTTP_400_BAD_REQUEST: {
            "description": "Item with such ID already exist",
            "model": schemas.Message,
        },
    },
)
async def create_item(
    item_in: schemas.ItemCreate,
    db: Session = Depends(get_db),
) -> schemas.Item:
    """
    Creates item using provided data.

    Args:
    item_in (schemas.ItemCreate):
        Represents data of provided item.
    db (Session, optional):
        Represents connection to database.

    Raises:
    HTTPException:
        Represents exception which raises in case Item with provided ID already exist.

    Returns:
    schemas.Item:
        Represents created Item.
    """
    item = models.Item(**item_in.model_dump())
    try:
        db.add(item)
        db.commit()
        db.refresh(item)
    except IntegrityError:
        raise HTTPException(status_code=HTTPStatus.HTTP_400_BAD_REQUEST, detail=f"Item with ID {id} already exist")

    return item


@items_router.put(
    path="/{id}",
    responses={
        HTTPStatus.HTTP_200_OK: {
            "description": "Successfully replaces item",
            "model": schemas.Item,
        },
        HTTPStatus.HTTP_404_NOT_FOUND: {
            "description": "Item with such ID wasn't found",
            "model": schemas.Message,
        },
    },
)
async def replace_item(
    id: int,
    item_in: schemas.ItemReplace,
    db: Session = Depends(get_db),
) -> schemas.Item:
    """
    Replaces existing item using provided data.

    Args:
    id (int):
        Represents id of item which has to be replaced.
    item_in (schemas.ItemReplace):
        Represents data which will replace the old one.
    db (Session, optional):
        Represents connection to database.

    Raises:
    HTTPException:
        Represents exception which raises in case Item with provided ID doesn't exist.

    Returns:
    schemas.Item:
        Represents replaced Item.
    """
    item = db.query(models.Item).filter(models.Item.id == id).first()
    if not item:
        raise HTTPException(status_code=HTTPStatus.HTTP_404_NOT_FOUND, detail=f"Item with ID {id} wasn't found")

    db.query(models.Item).filter(models.Item.id == id).update(item_in.model_dump(exclude_none=True))
    db.commit()
    db.refresh(item)

    return item


@items_router.patch(
    path="/{id}",
    responses={
        HTTPStatus.HTTP_200_OK: {
            "description": "Successfully patched item",
            "model": schemas.Item,
        },
        HTTPStatus.HTTP_404_NOT_FOUND: {
            "description": "Item with such ID wasn't found",
            "model": schemas.Message,
        },
        HTTPStatus.HTTP_304_NOT_MODIFIED: {
            "description": "Item with such ID wasn't modified",
        },
    },
)
async def update_item(
    id: int,
    item_in: schemas.ItemUpdate,
    db: Session = Depends(get_db),
) -> schemas.Item:
    """
    Updates fields of existed Item in database.

    Args:
    id (int):
        Represents id of item which has to be updated.
    item_in (schemas.ItemUpdate):
        Represents data which will update the old one.
    db (Session, optional):
        Represents connection to database.

    Raises:
    HTTPException:
        Represents exception which raises in case Item with provided ID doesn't exist or wasn't modified.

    Returns:
    schemas.Item:
        Represents updated Item.
    """
    item = db.query(models.Item).filter(models.Item.id == id).first()
    if not item:
        raise HTTPException(status_code=HTTPStatus.HTTP_404_NOT_FOUND, detail=f"Item with ID {id} wasn't found")
    if item.deleted:
        raise HTTPException(status_code=HTTPStatus.HTTP_304_NOT_MODIFIED)

    values = item_in.model_dump(exclude_none=True)
    if len(values) == 0:
        return item

    db.query(models.Item).filter(models.Item.id == id).update(values)
    db.commit()
    db.refresh(item)

    return item


@items_router.delete(
    path="/{id}",
    responses={
        HTTPStatus.HTTP_200_OK: {
            "description": "Successfully marked item as deleted",
            "model": schemas.Message,
        },
        HTTPStatus.HTTP_404_NOT_FOUND: {
            "description": "Item with such ID wasn't found",
            "model": schemas.Message,
        },
    },
)
async def delete_item(
    id: int,
    db: Session = Depends(get_db),
) -> schemas.Message:
    """
    Marks Item as deleted.

    Args:
    id (int):
        Represents ID of item which has to be marked as deleted.
    db (Session, optional):
        Represents connection to database.

    Raises:
    HTTPException:
        Represents exception which raises in case Item with provided ID doesn't exist.

    Returns:
    schemas.Message:
        Represents informational message.
    """
    item = db.query(models.Item).filter(models.Item.id == id).first()
    if not item:
        raise HTTPException(status_code=HTTPStatus.HTTP_404_NOT_FOUND, detail=f"Item with ID {id} wasn't found")

    item.deleted = True
    db.commit()

    return schemas.Message(message=f"Item with ID {id} has been marked as deleted")
