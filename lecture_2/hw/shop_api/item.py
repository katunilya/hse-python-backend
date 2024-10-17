from sqlalchemy.orm import Session
from typing import Optional
from fastapi import Query
from sqlalchemy import and_
from typing import List

from database import ItemTable
from schemes import Item

class CreateItem(Item):
    pass

class UpdateItem(Item):
    pass 


class ItemLogic():
    
    @staticmethod
    def update_data(db, query):
        
        db.commit()
        db.refresh(query)

    @staticmethod
    def create_item(db: Session, item: CreateItem):
        db_item = ItemTable(**item.model_dump())
        db.add(db_item)
        ItemLogic.update_data(db, db_item)
        #db.commit()
        #db.refresh()
        return db_item
    
    @staticmethod
    def get_item(db: Session, id: int):
        item = db.query(ItemTable).filter(ItemTable.id == id).first()
        return item
    
    @staticmethod
    def get_filtered_item(
        db: Session,
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        show_deleted: Optional[bool] = False):
        
        query = db.query(ItemTable).filter(ItemTable.deleted == False)
        if min_price:
            query = query.filter(ItemTable.price >= min_price)
        if max_price:
            query = query.filter(ItemTable.price <= max_price)
        if not show_deleted:
            query = query.filter(ItemTable.deleted == False)
        return query.offset(offset).limit(limit).all()
    
    @staticmethod
    def update(db: Session, id: int, item: UpdateItem):
        item_query = db.query(ItemTable).filter(and_ \
                      (ItemTable.id == id, ItemTable.deleted == False)).first()
        for key, value in item.model_dump(exclude_unset=True).items():
            setattr(item_query, key, value)
        ItemLogic.update_data(db, item_query)
        #db.commit()
        #db.refresh(query)
        return item_query
    
    @staticmethod
    def delete(db: Session, id: int):
        query = db.query(ItemTable).filter(ItemTable.id == id).first()
        query.deleted = True
        ItemLogic.update_data(db, query)
        return query