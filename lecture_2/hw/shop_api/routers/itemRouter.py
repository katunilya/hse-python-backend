from fastapi import APIRouter
from fastapi.responses import JSONResponse

from lecture_2.hw.shop_api.db import *

itemRouter = APIRouter(prefix="/item")


@itemRouter.post("/")
def postItem(item: ItemRequest = None):
    if item is None:
        id = createNewItemInItems()
        return JSONResponse(content={"id": id}, status_code=HTTPStatus.CREATED, headers={"location": f"/item/{id}"})
    else:
        item = addItemToItems(item)
        return JSONResponse(content=item.toResponse(), status_code=HTTPStatus.CREATED,
                            headers={"location": f"/item/{item.id}"})


@itemRouter.get("/{id}")
def getItem(id: int):
    try:
        return getItemById(id)
    except Exception:
        return JSONResponse(content={"error": "Item not found"}, status_code=HTTPStatus.NOT_FOUND)


@itemRouter.put("/{id}")
def replaceItem(id: int, item: ItemRequest = None):
    if item is not None:
        item = item.asItem()
    try:
        item = replaceItemWithId(id, item)
        return JSONResponse(content=item.toResponse(), status_code=HTTPStatus.OK)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail="Item not found")


@itemRouter.patch("/{id}")
def changeItem(id: int, newFields: dict = {}):
    try:
        for field in newFields.keys():
            if field not in ItemRequest.__fields__:
                raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Field not found")

        item = Item(
            id=newFields.get("id") or id,
            name=newFields.get("name"),
            price=newFields.get("price")
        )

        return changeItemWithId(id, item)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail="Item not modified")


@itemRouter.delete("/{id}")
def deleteItem(id: int):
    try:
        deleteItemFromItems(id)
    except Exception:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
