from http import HTTPStatus
from typing import Any

import pytest
from async_asgi_testclient import TestClient

from lecture_1.hw.math_plain_asgi import app


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/"),
        ("GET", "/not_found"),
        ("POST", "/"),
        ("POST", "/not_found"),
    ],
)
async def test_not_found(method: str, path: str):
    async with TestClient(app) as client:
        response = await client.open(
            path,
            method=method,
        )
        assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("query", "status_code"),
    [
        ({"n": ""}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"n": "lol"}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"x": "kek"}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"n": -1}, HTTPStatus.BAD_REQUEST),
        ({"n": 0}, HTTPStatus.OK),
        ({"n": 1}, HTTPStatus.OK),
        ({"n": 10}, HTTPStatus.OK),
    ],
)
async def test_factorial(query: dict[str, Any], status_code: int):
    async with TestClient(app) as client:
        # Форматируем строку запроса с параметрами
        query_string = "&".join(f"{
