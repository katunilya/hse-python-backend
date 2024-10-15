from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse

from lecture_4.demo_service.api.contracts import (
    RegisterUserRequest,
    UserResponse,
)
from lecture_4.demo_service.api.utils import (
    AdminDep,
    AuthorDep,
    UserServiceDep,
)
from lecture_4.demo_service.core.users import UserInfo, UserRole

router = APIRouter()


@router.post("/user-register")
async def register_user(
    body: RegisterUserRequest,
    user_service: UserServiceDep,
) -> UserResponse:
    entity = user_service.register(UserInfo(**body.model_dump()))
    return UserResponse.from_user_entity(entity)


@router.post("/user-get")
async def get_user(
    user_service: UserServiceDep,
    author: AuthorDep,
    id: Annotated[int | None, Query()] = None,
    username: Annotated[str | None, Query()] = None,
) -> UserResponse:
    if id is not None and username is not None:
        raise ValueError("both id and username are provided")

    if id is None and username is None:
        raise ValueError("neither id nor username are provided")

    if id is not None and (author.uid == id or author.info.role == UserRole.ADMIN):
        entity = user_service.get_by_id(id)
    elif author.info.username == username or author.info.role == UserRole.ADMIN:
        entity = user_service.get_by_username(username)

    if entity is None:
        raise HTTPException(HTTPStatus.NOT_FOUND)

    return UserResponse.from_user_entity(entity)


@router.post("/user-promote")
async def promote_user(
    id: Annotated[int, Query()], _: AdminDep, user_service: UserServiceDep
):
    user_service.grant_admin(id)
    return PlainTextResponse()
