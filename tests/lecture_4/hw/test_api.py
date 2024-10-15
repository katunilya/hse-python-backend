import pytest
from fastapi.testclient import TestClient
from lecture_4.demo_service.api.main import create_app
from fastapi import FastAPI


@pytest.fixture
def client():
    """
    Фикстура для создания тестового клиента FastAPI с правильной инициализацией.
    """
    app = FastAPI()
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_register_user_api(client):
    """
    Тест проверяет, что можно зарегистрировать пользователя через API.

    Успешность:
    - Запрос возвращает статус 200.
    - Ответ содержит корректный username пользователя.
    """
    response = client.post(
        "/user-register",
        json={
            "username": "testuser",
            "name": "Test User",
            "birthdate": "1990-01-01T00:00:00",
            "password": "ValidPassword123",
        },
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_get_user_api(client):
    """
    Тест проверяет, что можно получить информацию о пользователе по его username через API.

    Успешность:
    - Запрос возвращает статус 200.
    - Ответ содержит корректный username пользователя.
    """
    # Сначала регистрируем пользователя
    client.post(
        "/user-register",
        json={
            "username": "testuser",
            "name": "Test User",
            "birthdate": "1990-01-01T00:00:00",
            "password": "ValidPassword123",
        },
    )

    # Затем делаем запрос на получение информации
    response = client.post(
        "/user-get",
        params={"username": "testuser"},
        auth=("testuser", "ValidPassword123"),
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_get_user_api_both_id_and_username(client):
    """
    Тест проверяет, что при передаче одновременно и `id`, и `username`
    система выбрасывает ошибку с корректным сообщением.

    Успешность:
    - Запрос возвращает статус 400.
    - Сообщение об ошибке содержит "both id and username are provided".
    """
    # Регистрируем пользователя
    client.post(
        "/user-register",
        json={
            "username": "testuser",
            "name": "Test User",
            "birthdate": "1990-01-01T00:00:00",
            "password": "ValidPassword123",
        },
    )

    # Проверяем ошибку при передаче одновременно и id, и username
    response = client.post(
        "/user-get",
        params={"id": 1, "username": "testuser"},
        auth=("testuser", "ValidPassword123"),
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "both id and username are provided"}


def test_get_user_by_id_api(client):
    """
    Тест проверяет, что можно получить информацию о пользователе по его ID через API.

    Успешность:
    - Запрос возвращает статус 200.
    - Ответ содержит корректный username пользователя.
    """
    # Сначала регистрируем пользователя
    response = client.post(
        "/user-register",
        json={
            "username": "testuser",
            "name": "Test User",
            "birthdate": "1990-01-01T00:00:00",
            "password": "ValidPassword123",
        },
    )
    assert response.status_code == 200
    user_id = response.json()["uid"]

    # Затем делаем запрос на получение информации по ID
    response = client.post(
        "/user-get", params={"id": user_id}, auth=("testuser", "ValidPassword123")
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_get_user_both_id_and_username(client):
    """
    Тест проверяет, что система выбрасывает ошибку, если одновременно
    переданы и `id`, и `username`.

    Успешность:
    - Запрос возвращает статус 400.
    - Сообщение об ошибке содержит правильное описание.
    """
    # Сначала регистрируем пользователя
    client.post(
        "/user-register",
        json={
            "username": "testuser",
            "name": "Test User",
            "birthdate": "1990-01-01T00:00:00",
            "password": "ValidPassword123",
        },
    )

    # Пробуем передать и `id`, и `username`
    response = client.post(
        "/user-get",
        params={"id": 1, "username": "testuser"},
        auth=("testuser", "ValidPassword123"),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "both id and username are provided"


def test_get_user_neither_id_nor_username(client):
    """
    Тест проверяет, что система выбрасывает ошибку, если ни `id`, ни `username`
    не переданы.

    Успешность:
    - Запрос возвращает статус 400.
    - Сообщение об ошибке содержит правильное описание.
    """
    # Сначала регистрируем пользователя
    client.post(
        "/user-register",
        json={
            "username": "testuser",
            "name": "Test User",
            "birthdate": "1990-01-01T00:00:00",
            "password": "ValidPassword123",
        },
    )

    # Пробуем передать пустой запрос
    response = client.post("/user-get", auth=("testuser", "ValidPassword123"))
    assert response.status_code == 400
    assert response.json()["detail"] == "neither id nor username are provided"


def test_promote_user_to_admin(client):
    """
    Тест проверяет, что можно повысить пользователя до администратора.

    Успешность:
    - Запрос возвращает статус 200.
    - Пользователь становится администратором.
    """
    # Сначала регистрируем пользователя
    response = client.post(
        "/user-register",
        json={
            "username": "testuser",
            "name": "Test User",
            "birthdate": "1990-01-01T00:00:00",
            "password": "ValidPassword123",
        },
    )
    user_id = response.json()["uid"]

    # Промоутим пользователя в администраторы
    response = client.post(
        "/user-promote",
        params={"id": user_id},
        auth=("admin", "superSecretAdminPassword123"),
    )

    # Проверяем, что повышение прошло успешно
    assert response.status_code == 200


def test_get_user_by_id(client):
    """
    Тест проверяет, что можно получить информацию о пользователе по ID.

    Успешность:
    - Запрос возвращает статус 200.
    - Ответ содержит корректную информацию о пользователе.
    """
    # Регистрируем нового пользователя
    response = client.post(
        "/user-register",
        json={
            "username": "newuser",
            "name": "New User",
            "birthdate": "1995-01-01T00:00:00",
            "password": "ValidPassword123",
        },
    )
    user_id = response.json()["uid"]

    # Получаем информацию о пользователе по его ID
    response = client.post(
        "/user-get", params={"id": user_id}, auth=("newuser", "ValidPassword123")
    )

    # Проверяем, что запрос прошел успешно
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"


def test_value_error_handler(client):
    """
    Тест проверяет, что при возникновении ValueError возвращается правильный код и сообщение об ошибке.

    Успешность:
    - Код ответа 400.
    - Сообщение об ошибке корректно отображено.
    """
    # Сначала регистрируем пользователя
    client.post(
        "/user-register",
        json={
            "username": "testuser",
            "name": "Test User",
            "birthdate": "1990-01-01T00:00:00",
            "password": "ValidPassword123",
        },
    )

    # Пробуем вызвать ошибку ValueError через некорректный запрос
    response = client.post(
        "/user-get",
        params={"id": 1, "username": "testuser"},
        auth=("testuser", "ValidPassword123"),
    )

    # Проверяем, что возвращена корректная ошибка
    assert response.status_code == 400
    assert response.json()["detail"] == "both id and username are provided"


def test_get_non_existing_user(client):
    """
    Тест проверяет, что при запросе несуществующего пользователя возвращается статус 404.

    Успешность:
    - Код ответа 404.
    - Сообщение об ошибке: "Not Found".
    """
    # Пробуем получить несуществующего пользователя
    response = client.post(
        "/user-get",
        params={"username": "nonexistentuser"},
        auth=("admin", "superSecretAdminPassword123"),
    )

    # Проверяем, что возвращена ошибка 404
    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


def test_register_existing_username(client):
    """
    Тест проверяет, что нельзя зарегистрировать пользователя с уже существующим username.

    Успешность:
    - Запрос возвращает статус 400.
    - Сообщение об ошибке: "username is already taken".
    """
    # Сначала регистрируем пользователя
    client.post(
        "/user-register",
        json={
            "username": "testuser",
            "name": "Test User",
            "birthdate": "1990-01-01T00:00:00",
            "password": "ValidPassword123",
        },
    )

    # Пытаемся зарегистрировать пользователя с тем же username
    response = client.post(
        "/user-register",
        json={
            "username": "testuser",
            "name": "Another User",
            "birthdate": "1991-01-01T00:00:00",
            "password": "AnotherPassword123",
        },
    )

    # Проверяем, что возвращена ошибка 400
    assert response.status_code == 400
    assert response.json()["detail"] == "username is already taken"


def test_promote_non_existing_user(client):
    """
    Тест проверяет, что нельзя повысить до администратора несуществующего пользователя.

    Успешность:
    - Запрос возвращает статус 400.
    - Сообщение об ошибке: "user not found".
    """
    # Пытаемся повысить несуществующего пользователя в администраторы
    response = client.post(
        "/user-promote",
        params={"id": 999},
        auth=("admin", "superSecretAdminPassword123"),
    )

    # Проверяем, что возвращена ошибка 400
    assert response.status_code == 400
    assert response.json()["detail"] == "user not found"


def test_incorrect_password(client):
    """
    Тест проверяет, что система возвращает 401, если предоставлены некорректные учетные данные.

    Успешность:
    - Код ответа 401.
    - Сообщение об ошибке: "Unauthorized".
    """
    # Регистрируем пользователя
    client.post(
        "/user-register",
        json={
            "username": "testuser",
            "name": "Test User",
            "birthdate": "1990-01-01T00:00:00",
            "password": "ValidPassword123",
        },
    )

    # Пытаемся сделать запрос с неправильным паролем
    response = client.post(
        "/user-get", params={"username": "testuser"}, auth=("testuser", "WrongPassword")
    )

    # Проверяем, что возвращена ошибка 401
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"


def test_app_initialization():
    """
    Тест проверяет, что приложение FastAPI корректно инициализируется.

    Успешность:
    - Приложение создается без ошибок.
    """
    from lecture_4.demo_service.api.main import create_app

    app = create_app()

    assert app.title == "Testing Demo Service"


def test_requires_admin_access_denied(client):
    """
    Тест проверяет, что пользователю без прав администратора запрещен доступ к маршрутам,
    требующим административных прав.

    Успешность:
    - Пользователь без прав администратора не может получить доступ к административному маршруту.
    - Возвращается статус 403 (Forbidden).
    """
    # Регистрируем обычного пользователя
    client.post(
        "/user-register",
        json={
            "username": "normaluser",
            "name": "Normal User",
            "birthdate": "1995-01-01T00:00:00",
            "password": "Password123",
        },
    )

    # Пытаемся получить доступ к маршруту /user-promote как обычный пользователь (не администратор)
    response = client.post(
        "/user-promote",
        params={"username": "anotheruser"},
        auth=("normaluser", "Password123"),
    )

    # Проверяем, что доступ запрещен
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"
