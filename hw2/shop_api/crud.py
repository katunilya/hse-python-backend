from typing import Optional, List, Type
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from .models import Item


# CRUD for Item
def get_item(db: Session, item_id: int) -> Optional[models.Item]:
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def create_item(db: Session, item: schemas.ItemCreate) -> models.Item:
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, item_id: int, item: schemas.ItemCreate) -> Optional[models.Item]:
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        db_item.name = item.name
        db_item.price = item.price
        db.commit()
        db.refresh(db_item)
    return db_item


def soft_delete_item(db: Session, item_id: int) -> Optional[models.Item]:
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        db_item.deleted = True
        db.commit()
        db.refresh(db_item)
    return db_item


def get_items(
        db: Session,
        offset: int = 0,
        limit: int = 10,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        show_deleted: bool = False,
) -> list[Type[Item]]:
    query = db.query(models.Item)

    if min_price is not None:
        query = query.filter(models.Item.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Item.price <= max_price)

    if not show_deleted:
        query = query.filter(models.Item.deleted.is_(False))

    return query.offset(offset).limit(limit).all()


# CRUD for Cart
def create_cart(db: Session) -> models.Cart:
    db_cart = models.Cart(price=0.0)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart


def get_cart(db: Session, cart_id: int) -> Optional[models.Cart]:
    return db.query(models.Cart).filter(models.Cart.id == cart_id).first()


def add_item_to_cart(db: Session, cart_id: int, item_id: int, quantity: int = 1) -> Optional[models.Cart]:
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if cart and item:
        cart_item = models.CartItem(cart_id=cart_id, item_id=item_id, quantity=quantity, price=item.price)
        db.add(cart_item)
        db.commit()

        # Recalculate cart total price
        total_price = sum(ci.price * ci.quantity for ci in cart.items)
        cart.price = total_price
        db.commit()
        db.refresh(cart)

    return cart


def get_carts(
        db: Session,
        offset: int = 0,
        limit: int = 10,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_quantity: Optional[int] = None,
        max_quantity: Optional[int] = None,
) -> List[models.Cart]:
    query = db.query(models.Cart).join(models.CartItem)

    # Apply price filters
    if min_price is not None:
        query = query.filter(models.Cart.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Cart.price <= max_price)

    query = query.group_by(models.Cart.id)

    # Apply quantity filters
    if min_quantity is not None:
        query = query.having(func.sum(models.CartItem.quantity) >= min_quantity)
    if max_quantity is not None:
        query = query.having(func.sum(models.CartItem.quantity) <= max_quantity)

    return query.offset(offset).limit(limit).all()