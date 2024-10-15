from http import HTTPStatus
from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import NonNegativeInt, PositiveInt
from lecture_2.hw.shop_api.api.store import queries
from lecture_2.hw.shop_api.api.cart.contracts import CartResponse

router = APIRouter(prefix='/cart')

# POST add new cart
@router.post(
    '/', 
    status_code=HTTPStatus.CREATED,
    response_model=CartResponse
)
async def post_cart(response: Response) -> CartResponse:
    cart = queries.add_cart()
    response.headers['location'] = f'/cart/{cart.id}'
    return CartResponse.from_entity(cart)

# GET get cart
@router.get(
    '/{cart_id}',
    responses={
        HTTPStatus.OK: {
            'description': 'Successfully returned requested cart'
        },
        HTTPStatus.NOT_FOUND: {
            'description': 'Failed to return requested cart as one was not found'
        }
    },
    response_model=CartResponse
)
async def get_cart(cart_id: int) -> CartResponse:
    entity = queries.get_cart(id)

    if not entity:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f'Request resource /cart/{id} was not found'
        )
    
    return CartResponse.from_entity(entity)

# GET get cart list
@router.get('/', response_model=list)
async def get_carts(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: float = Query(None, ge=0),
    max_price: float = Query(None, ge=0),
    min_quantity: int = Query(None, ge=0),
    max_quantity: int = Query(None, ge=0)
) -> list[CartResponse]:
    
    entities = queries.get_carts(min_price, max_price, 
                                 min_quantity, max_quantity, 
                                 offset, limit)
    
    response = [CartResponse.from_entity(entity) for entity in entities]
    return response

# POST add item to cart
@router.post(
    '/{cart_id}/add/{item_id}',
    responses={
        HTTPStatus.OK: {
            'description': 'Successfully returned requested cart'
        },
        HTTPStatus.NOT_FOUND: {
            'description': 'Failed to return requested cart as one was not found'
        }
    },
    response_model=CartResponse,
)
async def add_item_to_cart(cart_id: int, item_id: int) -> CartResponse:
    cart = queries.add_item_to_cart(cart_id, item_id)
    if not cart:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f'Request resource /cart/{id} was not found'
        )
    return CartResponse.from_entity(cart)