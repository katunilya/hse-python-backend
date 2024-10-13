from contextlib import asynccontextmanager
from datetime import datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from lecture_4.demo_service.core.users import (
    UserEntity,
    UserInfo,
    UserRole,
    UserService,
    password_is_longer_than_8,
)


@asynccontextmanager
async def initialize(app: FastAPI):
    user_service = UserService(
        password_validators=[
            password_is_longer_than_8,
            lambda pwd: any(char.isdigit() for char in pwd),
        ]
    )
    user_service.register(
        UserInfo(
            username="admin",
            name="admin",
            birthdate=datetime.fromtimestamp(0.0),
            role=UserRole.ADMIN,
            password="superSecretAdminPassword123",
        )
    )

    app.state.user_service = user_service

    yield


def user_service(request: Request) -> UserService:
    return request.app.state.user_service


UserServiceDep = Annotated[UserService, Depends(user_service)]

security = HTTPBasic()
CredentialsDep = Annotated[HTTPBasicCredentials, Depends(security)]


def requires_author(
    credentials: CredentialsDep, user_service: UserServiceDep
) -> UserEntity:
    entity = user_service.get_by_username(credentials.username)

    if not entity or entity.info.password.get_secret_value() != credentials.password:
        raise HTTPException(HTTPStatus.UNAUTHORIZED)

    return entity


AuthorDep = Annotated[UserEntity, Depends(requires_author)]


def requires_admin(author: AuthorDep) -> UserEntity:
    if author.info.role != UserRole.ADMIN:
        raise HTTPException(HTTPStatus.FORBIDDEN)

    return author


AdminDep = Annotated[UserEntity, Depends(requires_admin)]


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(
        content={"detail": str(exc)},
        status_code=HTTPStatus.BAD_REQUEST,
    )
