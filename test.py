from http import HTTPStatus
from http.client import UNPROCESSABLE_ENTITY
from typing import Any
from uuid import uuid4

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from lecture_2.hw.shop_api.main import app

client = TestClient(app)

item = {"name": "test item", "price": 9.99}
response = client.post("/item", json=item)

assert response.status_code == HTTPStatus.CREATED
data = response.json()
print(data)
assert item["price"] == data["price"]
assert item["name"] == data["name"]