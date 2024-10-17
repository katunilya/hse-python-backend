from datetime import datetime
import pytest
from lecture_4.demo_service.api.main import create_app
from fastapi.testclient import TestClient
from lecture_4.demo_service.api.contracts import UserResponse, RegisterUserRequest, UserAuthRequest
from lecture_4.demo_service.core.users import UserInfo, UserRole, UserService, password_is_longer_than_8, UserEntity
from pydantic import  SecretStr



@pytest.fixture
def registration_req():
    return RegisterUserRequest(
        username="user",
        name="user",
        birthdate=datetime.now(),
        password=SecretStr("123456789")
    )

@pytest.fixture
def user_info():
    return UserInfo(
        username="user",
        name="user",
        birthdate=datetime.now(),
        role=UserRole.USER,
        password=SecretStr("123456798")
    )

@pytest.fixture
def entity(user_info):
    return UserEntity(
        uid=1,
        info=user_info
    )

@pytest.fixture
def service(entity):
    return UserService()

@pytest.fixture
def user_resp(entity):
    return UserResponse(
        uid=entity.uid,
        username=entity.info.username,
        name=entity.info.name,
        birthdate=entity.info.birthdate,
        role=entity.info.role
    )

@pytest.fixture
def user_auth_req() :
    return UserAuthRequest(
        username="user",
        password=SecretStr("moscow132")
    )

@pytest.fixture()
def client():
    new_app = create_app()
    with TestClient(new_app) as app:
        yield app

def test_password_is_longer_than_8():
    assert password_is_longer_than_8(SecretStr('123456798')) == True
    assert password_is_longer_than_8(SecretStr('123')) == False
    assert password_is_longer_than_8(SecretStr('')) == False



def test_register_user(client, user_info):
    registration_data = user_info.model_dump()
    registration_data["password"] = user_info.password.get_secret_value()
    registration_data["birthdate"] = user_info.birthdate.isoformat()


    response = client.post("/user-register", json=registration_data)
    assert response.status_code == 200
    assert response.json()["username"] == user_info.username
    assert response.json()["name"] == user_info.name
    assert response.json()["birthdate"] == user_info.birthdate.isoformat()
    assert response.json()["role"] == user_info.role

def test_password_reg(client, user_info):
    user_info.password = SecretStr("123")
    registration_data = user_info.model_dump()
    registration_data["password"] = user_info.password.get_secret_value()
    registration_data["birthdate"] = user_info.birthdate.isoformat()

    register_response = client.post("/user-register", json=registration_data)
    assert register_response.status_code == 400


def test_get_user_by_user(client, user_info, entity):
    registration_data = user_info.model_dump()
    registration_data["password"] = user_info.password.get_secret_value()
    registration_data["birthdate"] = user_info.birthdate.isoformat()
    credentials = (user_info.username, user_info.password.get_secret_value())

    registration_response = client.post("/user-register", json=registration_data)
    user_id = registration_response.json()["uid"]

    fetch_response = client.post("/user-get", params={'id': user_id}, auth=credentials)

    assert fetch_response.status_code == 200
    assert fetch_response.json()["name"] == user_info.name
    assert fetch_response.json()["username"] == user_info.username
    assert fetch_response.json()["role"] == user_info.role




    invalid_user_fetch_response = client.post(
        "/user-get",
        params={'id': entity.uid, 'username': entity.info.username}, auth=credentials
    )
    assert invalid_user_fetch_response.status_code == 400

    empty_params_response = client.post("/user-get", params={}, auth=credentials)
    assert empty_params_response.status_code == 400

    wrong_password_auth = (user_info.username, "wrong_password")
    unauthorized_response = client.post(
        "/user-get",
        params={'id': registration_response.json().get("uid")},
        auth=wrong_password_auth
    )
    assert unauthorized_response.status_code == 401

    non_existent_id_response = client.post("/user-get", params={'id': 9,'username': entity.info.username}, auth=credentials)
    assert non_existent_id_response.status_code == 400


def test_promote(client, user_info):
    registration_data = user_info.model_dump()
    registration_data["password"] = user_info.password.get_secret_value()
    registration_data["birthdate"] = user_info.birthdate.isoformat()
    credentials = (user_info.username, user_info.password.get_secret_value())

    register_response = client.post("/user-register", json=registration_data)
    assert register_response.status_code == 200

    promote_response = client.post("/user-promote", params={'id': register_response.json()["uid"]}, auth=credentials)
    assert promote_response.status_code == 403