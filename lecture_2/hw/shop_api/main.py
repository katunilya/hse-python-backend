from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi import Response
from http import HTTPStatus
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator

class CartItems(BaseModel): 
    
    id : int 
    name : str 
    quantity : int 
    available: bool  

class Cart(BaseModel): 

    id : int
    items : List[CartItems]
    price : float

class Item(BaseModel):

    id : int 
    name : str 
    price : float
    deleted : bool

class ItemPutRequest(BaseModel):
    name : str 
    price : float

class ItemPatchRequest(BaseModel):
    name : Optional[str | None] 
    price : Optional[float | None]

app = FastAPI()
Instrumentator().instrument(app).expose(app)

carts_base = dict()
items = dict()

def generate_id(): 
    counter = 0 
    while True: 
        yield counter 
        counter += 1

_generator_id = generate_id()
_generator_id_item = generate_id()

@app.post("/cart", 
          status_code=HTTPStatus.CREATED
)
async def get_cart_id(response: Response):
    id = next(_generator_id)
    cart = Cart(id=id, items=[], price=0)
    carts_base[id] = cart
    
    response.headers["Location"] = f"/cart/{id}"
    return cart


@app.get("/cart/{id}",
         responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested cart",
        },
        HTTPStatus.NOT_MODIFIED: {
            "description": "Failed to return requested cart as one was not found",
        },
    },)
async def get_cart_by_id(id : int):

    if id in carts_base: 
        return carts_base[id]
     
    return HTTPException(HTTPStatus.NOT_MODIFIED,
            f"Requested resource /cart/{id} was not found",)


@app.get("/cart", 
         responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested carts",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Some problems with query params",
        },   
         })
async def get_full_cart(offset: Optional[int] = 0,  
                        limit: Optional[int] = 10, 
                        min_price : Optional[int | None] = None,
                        max_price : Optional[int | None] = None,
                        min_quantity : Optional[int | None] = None,
                        max_quantity : Optional[int | None] = None):
    
   
    if (limit < 1) | (offset < 0):
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY)
        
    if (min_price is not None) and (min_price < 0):
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY)

    if (max_price is not None) and (max_price < 0): 
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY)

    if (min_quantity is not None) and (min_quantity < 0):
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY)

    if (max_quantity is not None) and (max_quantity < 0):
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY)

    bucket = []
    full_carts = list(carts_base.values()) 
    
    for x in full_carts:

        sum_item = 0
        for item in x.items: 
            sum_item += item.quantity

        if ((min_price is not None and x.price >= min_price) |
            (max_price is not None and x.price <= max_price) |
            (min_quantity is not None and sum_item >= min_quantity) |
            (max_quantity is not None and sum_item <= max_quantity) 
            ):

            bucket.append(x)
    
    return bucket[offset: offset+limit]


@app.post("/cart/{cart_id}/add/{item_id}", 
          responses={
        HTTPStatus.OK: {
            "description": "Successfully added item to cart",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "cart_id or item_id Not Found",
        },    
          })
async def add_item2cart(cart_id: int, item_id: int):

    if (cart_id not in carts_base) | (item_id not in items):
        return HTTPException(HTTPStatus.NOT_FOUND,
            f"Requested resource /cart/{cart_id}/add/{item_id} was not found",)
    
    #print(carts_base[cart_id])
    cart = carts_base[cart_id]
    print(cart)
    if len(cart.items) != 0:
        for x in cart.items:
            if item_id == x.id: 
                x.quantity += 1
                cart.price += items[item_id].price 
                return
    
    item_cart = items[item_id]
    carts_base[cart_id].items.append(CartItems(id=item_id, name=item_cart.name, quantity=1, available= not item_cart.deleted))
    carts_base[cart_id].price += item_cart.price


@app.post("/item", 
          status_code=HTTPStatus.CREATED)
async def add_item(item: ItemPutRequest):

    id = next(_generator_id_item)
    items[id] = Item(id=id, 
                     name=item.name,
                     price=item.price,
                     deleted=False)
    return items[id]


@app.get("/item/{id}",
         responses={
        HTTPStatus.OK: {
            "description": "Returned item by id"
            },
        HTTPStatus.NOT_FOUND: {
            "description": "Item was not founded"
            },
        HTTPStatus.NOT_MODIFIED: {
            "description": "Item was not modified"
            },
         })
async def get_item_by_id(id : int):

    if items[id].deleted == True: 
        raise HTTPException(HTTPStatus.NOT_FOUND,
            f"Requested resource /item/{id} was not found",)

    if id in items: 
        return items[id]
       
    return HTTPException(HTTPStatus.NOT_MODIFIED,
            f"Requested resource /item/{id} was not modified",)
 
    
@app.get("/item", 
         responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested items",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Some problems with query params",
        },   
         })
async def get_items(offset: Optional[int] = 0,
                    limit: Optional[int] = 10,
                    min_price: Optional[int | None] = None,
                    max_price: Optional[int | None] = None,
                    show_deleted: Optional[bool] = False):
    
    if (limit < 1) | (offset < 0):
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY)
        

    if (min_price is not None) and (min_price < 0):
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY)

    if (max_price is not None) and (max_price < 0): 
        raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY)

    bucket = []
    full_items = list(items.values()) 
    print(full_items)
    for x in full_items:

        if ((min_price is not None and x.price >= min_price) and
            (max_price is not None and x.price <= max_price) and
            (x.deleted == show_deleted) 
            ):

            bucket.append(x)
    print(bucket)
    return bucket[offset: offset+limit]


@app.put("/item/{id}", 
        responses={
        HTTPStatus.OK: {
            "description": "Successfully put item",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Item not in items",
        },   
         })
async def put_item(id: int, item: ItemPutRequest): 
    
    if id in items:
        items[id].name = item.name
        items[id].price = item.price
        return items[id]

    return HTTPStatus.UNPROCESSABLE_ENTITY


@app.patch("/item/{id}", 
        responses={
        HTTPStatus.OK: {
            "description": "Successfully patch item",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Item not in items",
        },
        HTTPStatus.NOT_MODIFIED: {
            "description": "Item was deleted",
        },   
         })
async def patch_item(id: int, item: dict[str, Any]): 
    
    patch_item = items.get(id)

    if patch_item.deleted:
        raise HTTPException(HTTPStatus.NOT_MODIFIED)

    for x in list(item.keys()): 
        if x not in ("name", "price"):
            raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY)

    if item.get("name") is not None:
        patch_item.name = item.get("name")
        items[id] = patch_item

    if item.get("price") is not None:
        patch_item.price = item.get("price")
        items[id] = patch_item

    return items[id]


@app.delete("/item/{id}",
         responses={
        HTTPStatus.OK: {
            "description": "Returned item by id"
            },
        HTTPStatus.NOT_FOUND: {
            "description": "Item was deleted"
            },
        })
async def delete_item(id: int): 
    
    if id in items: 
        items[id].deleted = True
        return HTTPStatus.OK
    
    raise HTTPException(HTTPStatus.NOT_FOUND)