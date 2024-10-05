from http import HTTPStatus
from http.client import UNPROCESSABLE_ENTITY
from typing import Any
from uuid import uuid4

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from lecture_2.hw.shop_api.main import app

client = TestClient(app)
faker = Faker()


# создает пустую корзину и возвращает её ID
@pytest.fixture()
def existing_empty_cart_id() -> int:
    return client.post("/cart").json()["id"]


# создает 10 товаров с фейковыми данными и возвращает список их ID
@pytest.fixture(scope="session")
def existing_items() -> list[int]:
    items = [
        {
            "name": f"Тестовый товар {i}",
            "price": faker.pyfloat(positive=True, min_value=10.0, max_value=500.0),
        }
        for i in range(10)
    ]

    return [client.post("/item", json=item).json()["id"] for item in items]


# создает 20 корзин, каждая с разным количеством товаров, и возвращает список ID этих корзин
@pytest.fixture(scope="session", autouse=True)
def existing_not_empty_carts(existing_items: list[int]) -> list[int]:
    carts = []

    for i in range(20):
        cart_id: int = client.post("/cart").json()["id"]
        for item_id in faker.random_elements(existing_items, unique=False, length=i):
            client.post(f"/cart/{cart_id}/add/{item_id}")

        carts.append(cart_id)

    return carts


# добавляет несколько товаров, созданных с помощью existing_items() в пустую корзину, созданную с помощью
# existing_empty_cart_id(), возвращая её ID.
@pytest.fixture()
def existing_not_empty_cart_id(
    existing_empty_cart_id: int,
    existing_items: list[int],
) -> int:
    for item_id in faker.random_elements(existing_items, unique=False, length=3):
        client.post(f"/cart/{existing_empty_cart_id}/add/{item_id}")

    return existing_empty_cart_id


# создает и возвращает один товар с фейковыми данными
@pytest.fixture()
def existing_item() -> dict[str, Any]:
    return client.post(
        "/item",
        json={
            "name": f"Тестовый товар {uuid4().hex}",
            "price": faker.pyfloat(min_value=10.0, max_value=100.0),
        },
    ).json()


# создает товар и сразу удаляет его, возвращая его данные
@pytest.fixture()
def deleted_item(existing_item: dict[str, Any]) -> dict[str, Any]:
    item_id = existing_item["id"]
    client.delete(f"/item/{item_id}")

    existing_item["deleted"] = True
    return existing_item


# Цель: Проверка создания новой корзины.
# Ожидания:
# Статус ответа должен быть 201 CREATED.
# Заголовок ответа должен содержать location (указание на URL новой корзины).
# В теле ответа должно быть поле id с идентификатором новой корзины.
@pytest.mark.xfail()
def test_post_cart() -> None:
    response = client.post("/cart")

    assert response.status_code == HTTPStatus.CREATED
    assert "location" in response.headers
    assert "id" in response.json()


# Цель: Проверка получения информации о корзине.
# Ожидания:
# Корзина может быть пустой или содержать товары (параметризовано).
# Если корзина не пуста, итоговая цена корзины должна быть рассчитана как сумма цен товаров, умноженных на их количество.
# Для пустой корзины цена должна быть 0.0.
@pytest.mark.xfail()
@pytest.mark.parametrize(
    ("cart", "not_empty"),
    [
        ("existing_empty_cart_id", False),
        ("existing_not_empty_cart_id", True),
    ],
)
def test_get_cart(request, cart: int, not_empty: bool) -> None:
    cart_id = request.getfixturevalue(cart)

    response = client.get(f"/cart/{cart_id}")

    assert response.status_code == HTTPStatus.OK
    response_json = response.json()

    len_items = len(response_json["items"])
    assert len_items > 0 if not_empty else len_items == 0

    if not_empty:
        price = 0

        for item in response_json["items"]:
            item_id = item["id"]
            price += client.get(f"/item/{item_id}").json()["price"] * item["quantity"]

        assert response_json["price"] == pytest.approx(price, 1e-8)
    else:
        assert response_json["price"] == 0.0


# Цель: Проверка фильтрации списка корзин.
# Ожидания:
# Поддержка фильтрации по следующим параметрам: offset, limit, min_price, max_price, min_quantity, max_quantity.
# Некорректные значения (например, отрицательные) должны возвращать статус 422 Unprocessable Entity.
# При корректных значениях фильтров ожидается успешный ответ 200 OK и проверка содержимого списка корзин.
@pytest.mark.xfail()
@pytest.mark.parametrize(
    ("query", "status_code"),
    [
        ({}, HTTPStatus.OK),
        ({"offset": 1, "limit": 2}, HTTPStatus.OK),
        ({"min_price": 1000.0}, HTTPStatus.OK),
        ({"max_price": 20.0}, HTTPStatus.OK),
        ({"min_quantity": 1}, HTTPStatus.OK),
        ({"max_quantity": 0}, HTTPStatus.OK),
        ({"offset": -1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"limit": 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"limit": -1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"min_price": -1.0}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"max_price": -1.0}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"min_quantity": -1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"max_quantity": -1}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ],
)
def test_get_cart_list(query: dict[str, Any], status_code: int):
    response = client.get("/cart", params=query)

    assert response.status_code == status_code

    if status_code == HTTPStatus.OK:
        data = response.json()

        assert isinstance(data, list)

        if "min_price" in query:
            assert all(item["price"] >= query["min_price"] for item in data)

        if "max_price" in query:
            assert all(item["price"] <= query["max_price"] for item in data)

        quantity = sum(item["quantity"] for cart in data for item in cart["items"])

        if "min_quantity" in query:
            assert quantity >= query["min_quantity"]

        if "max_quantity" in query:
            assert quantity <= query["max_quantity"]


# Цель: Проверка создания товара.
# Ожидания:
# Статус ответа должен быть 201 CREATED.
# В ответе должно возвращаться имя и цена созданного товара, которые должны совпадать с теми, что были отправлены в
# запросе.
@pytest.mark.xfail()
def test_post_item() -> None:
    item = {"name": "test item", "price": 9.99}
    response = client.post("/item", json=item)

    assert response.status_code == HTTPStatus.CREATED

    data = response.json()
    assert item["price"] == data["price"]
    assert item["name"] == data["name"]


# Цель: Проверка получения товара по его ID.
# Ожидания:
# Статус ответа должен быть 200 OK.
# Тело ответа должно содержать данные о товаре, и они должны совпадать с теми, которые были использованы при его создании.
@pytest.mark.xfail()
def test_get_item(existing_item: dict[str, Any]) -> None:
    item_id = existing_item["id"]

    response = client.get(f"/item/{item_id}")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == existing_item


# Цель: Проверка фильтрации списка товаров.
# Ожидания:
# Фильтрация по параметрам: offset, limit, min_price, max_price, show_deleted.
# Некорректные значения фильтров (например, отрицательные цены) должны возвращать 422 Unprocessable Entity.
# При корректных запросах ожидается успешный ответ с проверкой данных.
@pytest.mark.xfail()
@pytest.mark.parametrize(
    ("query", "status_code"),
    [
        ({"offset": 2, "limit": 5}, HTTPStatus.OK),
        ({"min_price": 5.0}, HTTPStatus.OK),
        ({"max_price": 5.0}, HTTPStatus.OK),
        ({"show_deleted": True}, HTTPStatus.OK),
        ({"offset": -1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"limit": -1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"limit": 0}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"min_price": -1}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"max_price": -1}, HTTPStatus.UNPROCESSABLE_ENTITY),
    ],
)
def test_get_item_list(query: dict[str, Any], status_code: int) -> None:
    response = client.get("/item", params=query)

    assert response.status_code == status_code

    if status_code == HTTPStatus.OK:
        data = response.json()

        assert isinstance(data, list)

        if "min_price" in query:
            assert all(item["price"] >= query["min_price"] for item in data)

        if "max_price" in query:
            assert all(item["price"] <= query["max_price"] for item in data)

        if "show_deleted" in query and query["show_deleted"] is False:
            assert all(item["deleted"] is False for item in data)


# Цель: Полное обновление данных товара.
# Ожидания:
# Если данные некорректны (например, не указано имя), статус должен быть 422 Unprocessable Entity.
# Если данные корректны, ответ должен быть 200 OK с обновленными данными товара.
@pytest.mark.xfail()
@pytest.mark.parametrize(
    ("body", "status_code"),
    [
        ({}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"price": 9.99}, HTTPStatus.UNPROCESSABLE_ENTITY),
        ({"name": "new name", "price": 9.99}, HTTPStatus.OK),
    ],
)
def test_put_item(
    existing_item: dict[str, Any],
    body: dict[str, Any],
    status_code: int,
) -> None:
    item_id = existing_item["id"]
    response = client.put(f"/item/{item_id}", json=body)

    assert response.status_code == status_code

    if status_code == HTTPStatus.OK:
        new_item = existing_item.copy()
        new_item.update(body)
        assert response.json() == new_item


# Цель: Частичное обновление данных товара.
# Ожидания:
# Если пытаются изменить удалённый товар, должен вернуться статус 304 Not Modified.
# Для существующего товара проверяется возможность изменения отдельных полей.
# Некорректные изменения (например, добавление поля odd или попытка установить флаг deleted) должны возвращать статус 422 Unprocessable Entity.
@pytest.mark.xfail()
@pytest.mark.parametrize(
    ("item", "body", "status_code"),
    [
        ("deleted_item", {}, HTTPStatus.NOT_MODIFIED),
        ("deleted_item", {"price": 9.99}, HTTPStatus.NOT_MODIFIED),
        ("deleted_item", {"name": "new name", "price": 9.99}, HTTPStatus.NOT_MODIFIED),
        ("existing_item", {}, HTTPStatus.OK),
        ("existing_item", {"price": 9.99}, HTTPStatus.OK),
        ("existing_item", {"name": "new name", "price": 9.99}, HTTPStatus.OK),
        (
            "existing_item",
            {"name": "new name", "price": 9.99, "odd": "value"},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
        (
            "existing_item",
            {"name": "new name", "price": 9.99, "deleted": True},
            HTTPStatus.UNPROCESSABLE_ENTITY,
        ),
    ],
)
def test_patch_item(request, item: str, body: dict[str, Any], status_code: int) -> None:
    item_data: dict[str, Any] = request.getfixturevalue(item)
    item_id = item_data["id"]
    response = client.patch(f"/item/{item_id}", json=body)

    assert response.status_code == status_code

    if status_code == HTTPStatus.OK:
        patch_response_body = response.json()

        response = client.get(f"/item/{item_id}")
        patched_item = response.json()

        assert patched_item == patch_response_body


# Цель: Проверка удаления товара.
# Ожидания:
# После удаления товара по его ID ответ должен быть 200 OK.
# При повторной попытке получить удалённый товар ожидается статус 404 Not Found.
# Повторное удаление должно возвращать 200 OK без ошибок.
@pytest.mark.xfail()
def test_delete_item(existing_item: dict[str, Any]) -> None:
    item_id = existing_item["id"]

    response = client.delete(f"/item/{item_id}")
    assert response.status_code == HTTPStatus.OK

    response = client.get(f"/item/{item_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND

    response = client.delete(f"/item/{item_id}")
    assert response.status_code == HTTPStatus.OK
