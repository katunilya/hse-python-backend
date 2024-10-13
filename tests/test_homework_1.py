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
        response = await client.get("/factorial", query_string=query)

    assert response.status_code == status_code
    if status_code == HTTPStatus.OK:
        assert "result" in response.json()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("params", "status_code"),
    [
        ("/lol", HTTPStatus.UNPROCESSABLE_ENTITY),
        ("/-1", HTTPStatus.BAD_REQUEST),
        ("/0", HTTPStatus.OK),
        ("/1", HTTPStatus.OK),
        ("/10", HTTPStatus.OK),
    ],
)
async def test_fibonacci(params: str, status_code: int):
    async with TestClient(app) as client:
        response = await client.get("/fibonacci" + params)

    assert response.status_code == status_code
    if status_code == HTTPStatus.OK:
        assert "result" in response.json()


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    ("json", "status_code"),
    [
        (None, HTTPStatus.UNPROCESSABLE_ENTITY),
        ([], HTTPStatus.BAD_REQUEST),
        ([1, 2, 3], HTTPStatus.OK),
        ([1, 2.0, 3.0], HTTPStatus.OK),
        ([1.0, 2.0, 3.0], HTTPStatus.OK),
    ],
)
async def test_mean(json: dict[str, Any] | None, status_code: int):
    async with TestClient(app) as client:
        response = await client.get("/mean", json=json)

    assert response.status_code == status_code
    if status_code == HTTPStatus.OK:
        assert "result" in response.json()
