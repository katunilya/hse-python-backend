from http import HTTPStatus
from typing import Annotated, List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import NonNegativeInt, PositiveInt
from lecture_2.hw.shop_api.api.store import queries
from lecture_2.hw.shop_api.api.item.contracts import ItemResponse, ItemRequest, ItemPatchRequest

router = APIRouter(prefix='/item')

# POST add new item
@router.post(
    '/', 
    status_code=HTTPStatus.CREATED,
    response_model=ItemResponse
)
async def post_item(response: Response) -> ItemResponse:
    item = queries.add_item()
    response.headers['location'] = f'/item/{item.id}'
    return ItemResponse.from_entity(item)

# GET get item
@router.get(
    '/{item_id}',
    responses={
        HTTPStatus.OK: {
            'description': 'Successfully returned requested item'
        },
        HTTPStatus.NOT_FOUND: {
            'description': 'Failed to return requested item as one was not found'
        }
    },
    response_model=ItemResponse
)
async def get_item(item_id: int) -> ItemResponse:
    entity = queries.get_item(id)

    if not entity:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f'Request resource /item/{id} was not found'
        )
    
    return ItemResponse.from_entity(entity)

# GET get item list
@router.get('/', response_model=List[ItemResponse])
async def get_items(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: float = Query(None, ge=0),
    max_price: float = Query(None, ge=0),
    show_deleted: bool = Query(False)
) -> list[ItemResponse]:
    
    entities = queries.get_items(min_price, max_price,
                                 offset, limit, show_deleted)
    
    response = [ItemResponse.from_entity(entity) for entity in entities]
    return response

# PUT replace item
@router.put(
        '/{id}', 
        response_model=ItemResponse,
        responses={
        HTTPStatus.OK: {
            'description': 'Successfully returned requested item'
        },
        HTTPStatus.NOT_FOUND: {
            'description': 'Failed to return requested item as one was not found'
        }
    })
async def replace_item(id: int, data: ItemRequest) -> ItemResponse:
    changed_item = queries.replace_item(id, data)
    if not changed_item:
        raise HTTPException(
            HTTPStatus.NOT_FOUND,
            f'Request resource /item/{id} was not found'
        )
    return ItemResponse.from_entity(changed_item)

# PATCH update item
@router.patch(
    '/{id}',
    responses={
     HTTPStatus.OK: {
         "description": "Data successfully modified"
         },
        HTTPStatus.NOT_FOUND: {
            "description": "Failed to return requested item as one was not found"
            },
        HTTPStatus.NOT_MODIFIED: {
            "description": "Failed to modify data as item is deleted or cannot be modified"
            },
    }   
)
async def patch_item(id: int, item_data: ItemPatchRequest) -> ItemResponse:
    try:
        patched_item = queries.patch_item(id, item_data)
        if not patched_item:
            raise HTTPException(
                HTTPStatus.NOT_FOUND,
                f'Request resource /item/{id} was not found'
            )
    except Exception:
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            'Failed to modify data'
        )
    return ItemResponse.from_entity(patched_item)
        

# DELETE delete item
@router.delete(
    '/{id}',
    responses={
        HTTPStatus.OK: {
            'description': 'Successfully returned requested item'
        },
        HTTPStatus.NOT_FOUND: {
            'description': 'Failed to return requested item as one was not found'
        }
    },
    status_code=HTTPStatus.OK
)
async def delete_item(id: int):
    entity = queries.delete_item(id)
    if not entity:
        raise HTTPException(
                HTTPStatus.NOT_FOUND,
                f'Request resource /item/{id} was not found'
            )
    return {'deleted': True}