from http import HTTPStatus
from typing import Iterable

from fastapi import HTTPException

from lecture_2.hw.shop_api.contracts.contracts import ItemRequest
from .models import Cart, Item

_carts = dict[int, Cart]()
_items = dict[int, Item]()


def createNewItemInItems() -> int:
    item = Item.createItem()
    _items[item.id] = item
    return item.id


def addItemToItems(itemRequest: ItemRequest):
    item = itemRequest.asItem()
    _items[item.id] = item
    return item


def getItemById(id: int) -> Item:
    if id not in _items.keys() or _items[id].deleted:
        raise Exception
    return _items[id].toResponse()


def createNewCartInCarts() -> int:
    cart = Cart.createCart()
    _carts[cart.id] = cart
    return cart.id


def getCartById(id) -> Cart:
    return _carts[id].toResponse()


def addItemToCart(cartId, itemId):
    cart = _carts[cartId]
    for item in cart.items:
        if item.id == itemId:
            item.quantity += 1
            cart.price += item.price
            break
    else:
        item = _items[itemId]
        cart.items.append(item.toCartItem())
        cart.price += item.price


def replaceItemWithId(itemId, item: Item = None):
    if not itemId in _items.keys():
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    if item is None:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Item not found")

    _items[itemId] = item
    return item


def deleteItemFromItems(itemId):
    _items[itemId].deleted = True
    return ItemRequest(
        id=_items[itemId].id,
        name=_items[itemId].name,
        price=_items[itemId].price,
        deleted=_items[itemId].deleted
    )


def changeItemWithId(itemId, item: Item):
    if not itemId in _items.keys() or _items[itemId].deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, detail="Item not found")
    _items[itemId].id = item.id or _items[itemId].id
    _items[itemId].name = item.name or _items[itemId].name
    _items[itemId].price = item.price or _items[itemId].price
    return ItemRequest(
        id=_items[itemId].id or itemId,
        name=_items[itemId].name,
        price=_items[itemId].price,
        deleted=_items[itemId].deleted
    )


def getCartList(offset: int, limit: int, min_price: float, max_price: float, min_quantity: int, max_quantity: int) -> \
Iterable[Cart]:
    result = []

    for cart in _carts.values():
        if min_price is not None and cart.price < min_price:
            continue
        if max_price is not None and cart.price > max_price:
            continue

        if min_quantity is not None and sum(item.quantity for item in cart.items) < min_quantity:
            continue
        if max_quantity is not None and sum(item.quantity for item in cart.items) > max_quantity:
            continue

        result.extend([item.toResponse() for item in cart.items[offset:offset + limit]])

    return result
