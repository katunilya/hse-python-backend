"""
Эти тесты проверяют работу сервиса пользователей (UserService), который включает в себя регистрацию пользователей,
валидацию паролей, получение информации о пользователях и повышение их прав до администратора.
"""

import pytest
from lecture_4.demo_service.core.users import (
    UserService,
    UserInfo,
    UserRole,
    password_is_longer_than_8,
)
from pydantic import SecretStr
from datetime import datetime


@pytest.fixture
def user_service():
    """
    Фикстура для создания экземпляра UserService с валидаторами:
    - Проверка длины пароля (больше 8 символов).
    - Проверка наличия хотя бы одной цифры в пароле.
    """
    return UserService(
        password_validators=[
            password_is_longer_than_8,
            lambda pwd: any(char.isdigit() for char in pwd),
        ]
    )


def test_register_user(user_service):
    """
    Тест проверяет, что пользователь успешно регистрируется, и ему присваивается уникальный ID.

    Успешность:
    - Пользователь успешно регистрируется.
    - Проверяется, что UID равен 1 и username соответствует ожиданиям.
    """
    user_info = UserInfo(
        username="testuser",
        name="Test User",
        birthdate=datetime(1990, 1, 1),
        role=UserRole.USER,
        password=SecretStr("ValidPassword123"),
    )
    user = user_service.register(user_info)
    assert user.uid == 1
    assert user.info.username == "testuser"


@pytest.mark.parametrize(
    "password,expected_exception",
    [
        ("short", ValueError),  # слишком короткий пароль
        ("no_digit_password", ValueError),  # нет цифр
    ],
)
def test_register_user_with_invalid_password(
    user_service, password, expected_exception
):
    """
    Тест проверяет, что система корректно выбрасывает исключение, если пароль
    не соответствует требованиям (короткий пароль или отсутствие цифр).

    Успешность:
    - Если пароль слишком короткий или не содержит цифр, выбрасывается ValueError.
    """
    user_info = UserInfo(
        username="shortpassuser",
        name="Short Password User",
        birthdate=datetime(1990, 1, 1),
        role=UserRole.USER,
        password=SecretStr(password),
    )
    with pytest.raises(expected_exception):
        user_service.register(user_info)


def test_get_user_by_username(user_service):
    """
    Тест проверяет, что метод `get_by_username` корректно возвращает
    пользователя по имени, если пользователь существует, и возвращает
    None, если пользователь с таким именем не найден.

    Успешность:
    - Пользователь найден: возвращает объект UserEntity.
    - Пользователь не найден: возвращает None.
    """
    # Создаем пользователя
    user_info = UserInfo(
        username="testuser",
        name="Test User",
        birthdate=datetime(1990, 1, 1),
        role=UserRole.USER,
        password=SecretStr("ValidPassword123"),
    )
    user_service.register(user_info)

    # Проверяем, что пользователь найден
    user = user_service.get_by_username("testuser")
    assert user is not None
    assert user.info.username == "testuser"

    # Проверяем, что пользователь с несуществующим именем не найден
    user_not_found = user_service.get_by_username("nagibator2008")
    assert user_not_found is None


def test_get_user_by_id(user_service):
    """
    Тест проверяет, что метод `get_by_id` корректно возвращает
    пользователя по его ID, если пользователь существует, и возвращает
    None, если пользователь с таким ID не найден.

    Успешность:
    - Пользователь найден: возвращает объект UserEntity.
    - Пользователь не найден: возвращает None.
    """
    # Создаем пользователя
    user_info = UserInfo(
        username="testuser",
        name="Test User",
        birthdate=datetime(1990, 1, 1),
        role=UserRole.USER,
        password=SecretStr("ValidPassword123"),
    )
    user = user_service.register(user_info)

    # Проверяем, что пользователь найден по ID
    found_user = user_service.get_by_id(user.uid)
    assert found_user is not None
    assert found_user.uid == user.uid

    # Проверяем, что пользователь с несуществующим ID не найден
    user_not_found = user_service.get_by_id(999)
    assert user_not_found is None


def test_grant_admin(user_service):
    """
    Тест проверяет, что метод `grant_admin` корректно изменяет роль
    пользователя на администратора. Также проверяется выбрасывание
    исключения, если пользователь не найден.

    Успешность:
    - Роль пользователя изменена на ADMIN.
    - Если пользователь не найден, выбрасывается ValueError.
    """
    # Создаем пользователя
    user_info = UserInfo(
        username="regularuser",
        name="Regular User",
        birthdate=datetime(1990, 1, 1),
        role=UserRole.USER,
        password=SecretStr("ValidPassword123"),
    )
    user = user_service.register(user_info)

    # Повышаем права до администратора
    user_service.grant_admin(user.uid)

    # Проверяем, что роль пользователя изменена
    assert user_service.get_by_id(user.uid).info.role == UserRole.ADMIN

    # Проверяем, что выбрасывается исключение, если пользователь не найден
    with pytest.raises(ValueError, match="user not found"):
        user_service.grant_admin(999)


def test_register_existing_user(user_service):
    """
    Тест проверяет, что метод `register` выбрасывает исключение, если
    пользователь с таким именем уже существует.

    Успешность:
    - Если имя пользователя уже зарегистрировано, выбрасывается ValueError.
    """
    # Регистрируем пользователя
    user_info = UserInfo(
        username="testuser",
        name="Test User",
        birthdate=datetime(1990, 1, 1),
        role=UserRole.USER,
        password=SecretStr("ValidPassword123"),
    )
    user_service.register(user_info)

    # Попытка зарегистрировать пользователя с тем же именем
    with pytest.raises(ValueError, match="username is already taken"):
        user_service.register(user_info)


@pytest.mark.parametrize(
    "password,expected_exception",
    [
        ("ValidPassword123", None),  # Валидный пароль
        ("NoDigitsHere", ValueError),  # Нет цифр
    ],
)
def test_password_requires_digit(user_service, password, expected_exception):
    """
    Тест проверяет, что валидатор пароля отклоняет пароли, которые не содержат
    хотя бы одну цифру.

    Успешность:
    - Валидный пароль проходит регистрацию.
    - Пароль без цифр выбрасывает ValueError.
    """
    user_info = UserInfo(
        username="testuser",
        name="Test User",
        birthdate=datetime(1990, 1, 1),
        role=UserRole.USER,
        password=SecretStr(password),
    )

    if expected_exception:
        with pytest.raises(expected_exception):
            user_service.register(user_info)
    else:
        user_service.register(user_info)  # Пароль валиден, исключений нет
