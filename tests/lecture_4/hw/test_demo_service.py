from datetime import datetime
from datetime import timedelta
from typing import Any

import pytest
from starlette.testclient import TestClient

from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.api.contracts import RegisterUserRequest, UserResponse, UserAuthRequest, SecretStr
from lecture_4.demo_service.core.users import UserInfo, UserService, UserEntity, UserRole, password_is_longer_than_8



def decode_model(user_info: UserInfo) -> dict[str, Any]:
    request_dict = user_info.model_dump()
    request_dict["password"] = user_info.password.get_secret_value()
    request_dict["birthdate"] = user_info.birthdate.isoformat()
    return request_dict


demo_service = create_app()
client = TestClient(demo_service)

@pytest.fixture
def short_password() -> SecretStr:
    return SecretStr("short")

@pytest.fixture
def long_password() -> SecretStr:
    return SecretStr("long_password_123")

@pytest.fixture
def register_user() -> RegisterUserRequest:
    return RegisterUserRequest(
        username="user",
        name="user",
        birthdate=datetime.now(),
        password=SecretStr("secret_password_123")
    )

@pytest.fixture
def user_info() -> UserInfo:
    return UserInfo(
        username="user",
        name="user",
        birthdate=datetime.now(),
        role=UserRole.USER,
        password="secret_password_123"
    )

@pytest.fixture
def admin_user_info() -> UserInfo:
    return UserInfo(
        username="admin",
        name="admin",
        birthdate=datetime.fromtimestamp(0.0),
        role=UserRole.ADMIN,
        password="superSecretAdminPassword123",
    )

@pytest.fixture
def bad_password_user_info(short_password) -> UserInfo:
    return UserInfo(
        username="test",
        name="test",
        birthdate=datetime.fromtimestamp(0.0),
        role=UserRole.USER,
        password=short_password,
    )
    
@pytest.fixture
def user_entity(user_info) -> UserEntity:
    return UserEntity(
        uid=1,
        info=user_info
    )

@pytest.fixture
def user_service(user_entity) -> UserService:
    return UserService()

@pytest.fixture
def user_response(user_entity) -> UserResponse:
    return UserResponse(
        uid=user_entity.uid,
        username=user_entity.info.username,
        name=user_entity.info.name,
        birthdate=user_entity.info.birthdate,
        role=user_entity.info.role
    )

@pytest.fixture
def user_auth_request() -> UserAuthRequest:
    return UserAuthRequest(
        username="user",
        password=SecretStr("secret_password_123")
    )

@pytest.fixture()
def demo_service_client():
    demo_app = create_app()
    with TestClient(demo_app) as demo_app_client:
        yield demo_app_client


def test_password_is_longer_than_8(short_password, long_password):
    assert password_is_longer_than_8(long_password) == True
    assert password_is_longer_than_8(short_password) == False

def test_user_auth(user_auth_request):
    assert user_auth_request.username == "user"
    assert user_auth_request.password.get_secret_value() == "secret_password_123"

def test_register_user(register_user):
    assert register_user.username == "user"
    assert register_user.name == "user"
    assert register_user.password.get_secret_value() == "secret_password_123"
    assert register_user.birthdate > datetime.now() - timedelta(seconds=1)

def test_user_info(user_info):
    assert user_info.username == "user"
    assert user_info.name == "user"
    assert user_info.birthdate > datetime.now() - timedelta(seconds=1)
    assert user_info.password.get_secret_value() == "secret_password_123"
    assert user_info.role == UserRole.USER

def test_user_entity(user_entity, user_info):
    assert user_entity.uid == 1
    assert user_entity.info == user_info

def test_user_response(user_response, user_entity):
    assert user_response.uid == 1
    assert user_response.username == "user"
    assert user_response.name == "user"
    assert user_response.birthdate > datetime.now() - timedelta(seconds=1)
    assert user_response.role == UserRole.USER

    user_response_from_entity = UserResponse.from_user_entity(user_entity)
    assert user_response_from_entity.uid == 1
    assert user_response_from_entity.username == "user"
    assert user_response_from_entity.name == "user"
    assert user_response_from_entity.birthdate > datetime.now() - timedelta(seconds=1)
    assert user_response_from_entity.role == UserRole.USER

def test_user_service(user_service, user_info):
    user_entity = user_service.register(user_info)
    assert user_entity.info.username == "user"
    assert user_entity.info.name == "user"
    assert user_entity.info.birthdate > datetime.now() - timedelta(seconds=1)
    assert user_entity.info.password.get_secret_value() == "secret_password_123"
    assert user_entity.info.role == UserRole.USER

    assert user_service.get_by_username(user_entity.info.username) == user_entity
    assert user_service.get_by_id(user_entity.uid) == user_entity

    user_service.grant_admin(user_entity.uid)
    assert user_service.get_by_id(user_entity.uid).info.role == UserRole.ADMIN

    with pytest.raises(ValueError):
        assert user_service.grant_admin('no_such_user')
    
    user_service.get_by_username("no_such_user") == None

def test_bad_password_registration(demo_service_client, bad_password_user_info):
    request_data = decode_model(bad_password_user_info)

    register_response = demo_service_client.post("/user-register", json=request_data)
    assert register_response.status_code == 400

def test_register_user(demo_service_client, register_user):
    request_dict = decode_model(register_user)

    response = demo_service_client.post("/user-register", json=request_dict)
    assert response.status_code == 200

    assert response.json()["username"] == register_user.username
    assert response.json()["name"] == register_user.name
    assert response.json()["birthdate"] == register_user.birthdate.isoformat()
    assert response.json()["role"] == UserRole.USER.value

def test_get_user_by_user(demo_service_client, register_user, user_entity, user_response):
    request_data = decode_model(register_user)
    auth = (register_user.username, register_user.password.get_secret_value())

    register_response = demo_service_client.post("/user-register", json=request_data)
    response = demo_service_client.post("/user-get", params={'id': register_response.json()["uid"]}, auth=auth)

    assert response.status_code == 200
    assert response.json()["name"] == user_response.name
    assert response.json()["username"] == user_response.username
    assert response.json()["role"] == user_response.role
    assert datetime.fromisoformat(response.json()["birthdate"]) > user_response.birthdate - timedelta(seconds=1)

    response = demo_service_client.post("/user-get", params={'id': user_entity.uid, 'username': user_entity.info.username}, auth=auth)
    assert response.status_code == 400

    response = demo_service_client.post("/user-get", params={}, auth=auth)
    assert response.status_code == 400

    auth = (register_user.username, "wrong_password")
    response = demo_service_client.post("/user-get", params={'id': register_response.json().get("uid")}, auth=auth)
    assert response.status_code == 401

def test_get_user_by_admin(demo_service_client, admin_user_info):
    admin_requets_dict = decode_model(admin_user_info)
    admin_auth = (admin_user_info.username, admin_user_info.password.get_secret_value())

    demo_service_client.post("/user-register", json=admin_requets_dict)
    response = demo_service_client.post("/user-get", params={"username": "test"}, auth=admin_auth)
    assert response.status_code == 404
        
    demo_service_client.post("/user-register", json=admin_requets_dict)
    response = demo_service_client.post("/user-get", params={"username": "admin"}, auth=admin_auth)
    assert response.status_code == 200

def test_promote_user_by_user(demo_service_client, register_user):
    request_data = decode_model(register_user)
    auth = (register_user.username, register_user.password.get_secret_value())

    register_response = demo_service_client.post("/user-register", json=request_data)
    assert register_response.status_code == 200

    promote_response = demo_service_client.post("/user-promote", params={'id': register_response.json()["uid"]}, auth=auth)
    assert promote_response.status_code == 403

def test_promote_user_by_admin(demo_service_client, admin_user_info):
    admin_auth = (admin_user_info.username, admin_user_info.password.get_secret_value())

    promote_response = demo_service_client.post("/user-promote", params={'id': "1"}, auth=admin_auth)
    assert promote_response.status_code == 200
        