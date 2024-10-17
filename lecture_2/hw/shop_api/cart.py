from statistics import quantiles
from typing import Optional
from fastapi import Query
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import CartTable, connect_table

class CartLogic():
    
    @staticmethod        
    def create_cart(db: Session):
        
         cart = CartTable()
         db.add(cart)
         db.commit()
         db.refresh(cart)
         return cart
        
        
    @staticmethod
    def get_cart(db: Session, id: int):
        cart = db.query(CartTable).filter(CartTable.id == id).first()
        for item in cart.items:
            item_counter = len(cart.items)
            if item_counter != 0:
                row = db.query(connect_table).filter_by(cart_id = id).first()
                item.quantity = row.quantity
            else:
                return cart
        return cart
    
    @staticmethod
    def item_counter(query, mn, mx):
        return query.group_by(CartTable.id).having(func.sum(connect_table.c.quantity) >= mn if mn else True). \
               having(func.sum(connect_table.c.quantity) <= mx if mx else True)
    
    @staticmethod
    def get_filtered_carts(
        db: Session, 
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_quantity: Optional[float] = None,
        max_quantity: Optional[float] = None):
        
        query = db.query(CartTable)
        if min_price: 
            query = query.filter(CartTable.price >= min_price)
        if max_price:
            query = query = query.filter(CartTable.price <= max_price)
        if max_quantity == 0:
            query = query.filter(CartTable.items == None)
        
        query = query.join(connect_table)
        query = CartLogic.item_counter(query, min_quantity, max_quantity)
        
        return query.offset(offset).limit(limit).all()
    
    @staticmethod
    def put_item_into_cart(db: Session, cart_id: int, item_id:int):
        cart = CartLogic.get_cart(db, cart_id)
        row = (db.query(connect_table). \
               filter(connect_table.c.cart_id == cart_id). \
               filter(connect_table.c.item_id == item_id).first())
        item_counter = 1
        if row:
            item_counter = row.quantity + 1
            db.query(connect_table). \
                filter((connect_table.c.cart_id == cart_id) & \
                      (connect_table.c.item_id == item_id)). \
                update({connect_table.c.quantity: item_counter})
        else:
            update_connection_table = connect_table.insert().values(
                                        cart_id = cart_id, 
                                        item_id = item_id,
                                        quantity = item_counter
                                        )
            db.execute(update_connection_table)
        
        return cart
    
    @staticmethod
    def update_price(db: Session, id: int):
        cart = CartLogic.get_cart(db, id)
        price = 0
        for item in cart.items:
            price += item.price * item.quantity
        cart.price = price
        db.add(cart)
        db.commit()