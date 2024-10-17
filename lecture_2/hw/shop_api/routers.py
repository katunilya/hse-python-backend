
from fastapi import APIRouter, Query, Depends, Body, HTTPException, status
from typing import Optional, List
from fastapi.responses import JSONResponse
from http import HTTPStatus

from pydantic import Json
from schemes import CartItem, Cart, Item, EmptyItem
from sqlalchemy.orm import Session
from database import Base
from connection import get_session, engine
from cart import CartLogic
from item import ItemLogic, CreateItem, UpdateItem

Base.metadata.create_all(bind=engine)


shop_router = APIRouter()
#item_router = APIRouter()

    

@shop_router.post("/cart", response_model=Cart)
def create_cart(db: Session = Depends(get_session)):
    cart = CartLogic.create_cart(db=db)
    
    return JSONResponse(
            content = {"id": cart.id},
            status_code= HTTPStatus.CREATED,
            headers = {"location": f'/cart/{cart.id}'}            
        )
 
@shop_router.get("/cart/{id}", response_model=Cart)
def get_cart_by_id(id: int, db: Session = Depends(get_session)):
    CartLogic.update_price(db=db, id=id)
    cart = CartLogic.get_cart(db=db, id=id)
    if not cart:
        return JSONResponse(
            status_code = HTTPStatus.NOT_FOUND,
            content = {"id":id, "error": f'Cart {id} not found'})
    else:
        return cart
       

@shop_router.get("/cart", response_model=List[Cart])
def get_cart(db: Session = Depends(get_session),
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_quantity: Optional[float] = None,
        max_quantity: Optional[float] = None,
    ):
        
    if offset < 0 or limit <= 0 or \
    (min_price is not None and min_price < 0) or \
    (max_price is not None and max_price <= 0) or \
    (min_quantity is not None and min_quantity < 0) or \
    (max_quantity is not None and max_quantity < 0):
        return JSONResponse(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content = {"error":"wrong parameters"}
           )  
    carts = CartLogic.get_filtered_carts(db=db, limit=limit, min_price=min_price,
                                         max_price=max_price, min_quantity=min_quantity,
                                         max_quantity=max_quantity)
    return carts
    

@shop_router.post("/cart/{cart_id}/add/{item_id}")
def add_item(cart_id: int, item_id: int, db: Session = Depends(get_session)):
    query_cart = CartLogic.get_cart(db=db, id=cart_id)
    query_item = ItemLogic.get_item(db=db, id=item_id)
    if query_cart is None:
        return JSONResponse(
            status_code = HTTPStatus.NOT_FOUND,
            content={"error":f'Cart {cart_id} not found or deleted'}
            )
    if query_item is None:
        return JSONResponse(
            status_code = HTTPStatus.NOT_FOUND,
            content={"error":f'Item {item_id} not found or deleted'}
            )
    cart = CartLogic.put_item_into_cart(db, cart_id, item_id)
    CartLogic.update_price(db=db, id = cart_id)
    return cart
    
@shop_router.post("/item", response_model=CartItem)  
def create_item(item: CreateItem, db: Session=Depends(get_session)):
    new_item = ItemLogic.create_item(db=db, item=item)
    return JSONResponse (
            content = {"id": new_item.id, "name": new_item.name, "price": new_item.price},
            status_code = HTTPStatus.CREATED,
            headers =  {"location": f'/item/{new_item.id}'} 
        )

@shop_router.get("/item/{id}", response_model = CartItem)
def get_item_by_id(id: int, db: Session = Depends(get_session)):
    item = ItemLogic.get_item(db=db, id=id)
    if item is None or item.deleted:
        return JSONResponse(
            status_code = HTTPStatus.NOT_FOUND,
            content = {"id":id, "error": f'Item {id} not found'})
    return JSONResponse(
            status_code = HTTPStatus.OK,
            content = {"id":item.id, "name": item.name, "price":item.price})

@shop_router.get("/item", response_model=List[CartItem])
def get_items(
    offset: Optional[int] = 0,
    limit: Optional[int] = 10,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    show_deleted: bool = False,
    db: Session = Depends(get_session)):
    
    if offset < 0 or limit <= 0 or \
    (min_price is not None and min_price < 0) or \
    (max_price is not None and max_price <= 0):
        return JSONResponse (
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                content = {"error":"wrong parameters"}
            )
    items = ItemLogic.get_filtered_item(db=db, offset = offset, limit=limit,
                                        min_price=min_price, max_price=max_price,
                                        show_deleted=show_deleted)
    return items

@shop_router.put("/item/{id}", response_model=CartItem)
def update_item(id: int, item: Item, db: Session = Depends(get_session)):
    current_item = ItemLogic.update(db=db, id = id, item=item)
    if current_item is None:
        return JSONResponse(
            status_code = HTTPStatus.NOT_FOUND,
            content={"error":f'Item {id} not found or deleted'}
            )
    return JSONResponse(
            content = {"id":current_item.id, "name":current_item.name, "price":current_item.price},
            status_code=HTTPStatus.OK
            )

@shop_router.patch("/item/{id}", response_model=EmptyItem)
def patch_item(id: int, data = Body(), db: Session = Depends(get_session)):
    item = ItemLogic.get_item(db, id = id)
    if item is None:
        return JSONResponse(
            status_code= HTTPStatus.NOT_FOUND,
            content= {"error":"not found"}
            )
    if data is None and item.deleted is False:
        return JSONResponse(
            content= {"id":item.id, "name":item.name, "price":item.price},
             status_code= HTTPStatus.OK
            )
    if item.deleted:
        return JSONResponse(
            status_code = HTTPStatus.NOT_MODIFIED,
            content= {"error":"cannot make item deleted"}
            )
    
    fields = set(["name", "price"])
    for field in data:
        if field not in fields:
            return JSONResponse(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                content = {"error": f'Unposible add field {field}'}
                )
    
    patched_data = data
    for key, value in patched_data.items():
        setattr(item, key, value)
    
    ItemLogic.update_data(db, item)
    return JSONResponse(
            status_code=HTTPStatus.OK,
            content = {"id":item.id, "name":item.name, "price":item.price}
        )

@shop_router.delete("/item/{id}", response_model=CartItem)
def delete_item(id: int, db: Session = Depends(get_session)):
    item = ItemLogic.get_item(db = db, id = id)
    if item.deleted is True:
        return JSONResponse(
                status_code=HTTPStatus.NOT_FOUND,
                content= {"error":"not found"}
            )
    else:
        deleted_item = ItemLogic.delete(db=db, id = id)
        return deleted_item