import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from lecture_4.demo_service.api.main import create_app


@pytest.fixture(scope="module")
def test_client():
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_register_user_success(test_client):
    response = test_client.post(
        "/user-register",
        json={
            "username": "testuser",
            "name": "Test User",
            "birthdate": "1990-01-01T00:00:00",
            "password": "testPassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["name"] == "Test User"
    assert data["role"] == "user"
    assert "uid" in data


def test_register_user_duplicate_username(test_client):
    response = test_client.post(
        "/user-register",
        json={
            "username": "duplicateuser",
            "name": "User One",
            "birthdate": "1991-01-01T00:00:00",
            "password": "Password1234",
        },
    )
    assert response.status_code == 200

    response = test_client.post(
        "/user-register",
        json={
            "username": "duplicateuser",
            "name": "User Two",
            "birthdate": "1992-02-02T00:00:00",
            "password": "Password5678",
        },
    )
    assert response.status_code == 400
    data = response.json()
    assert "username is already taken" in data["detail"]


@pytest.mark.xfail(reason="app allows to register a user with empty username")
def test_register_user_empty_username(test_client):
    response = test_client.post(
        "/user-register",
        json={
            "username": "",
            "name": "Empty Username User",
            "birthdate": "1993-03-03T00:00:00",
            "password": "Password1234",
        },
    )
    assert response.status_code == 422


def test_register_user_invalid_birthdate(test_client):
    response = test_client.post(
        "/user-register",
        json={
            "username": "invalidbirthdate",
            "name": "Invalid Birthdate User",
            "birthdate": "not-a-date",
            "password": "Password1234",
        },
    )
    assert response.status_code == 422


def test_register_user_future_birthdate(test_client):
    future_date = (datetime.now().replace(year=datetime.now().year + 1)).isoformat()
    response = test_client.post(
        "/user-register",
        json={
            "username": "futureuser",
            "name": "Future User",
            "birthdate": future_date,
            "password": "Password1234",
        },
    )
    assert response.status_code == 200


@pytest.mark.xfail(reason="app do not allow to register a user with long password")
def test_register_user_long_password(test_client):
    long_password = "P" * 10e6
    response = test_client.post(
        "/user-register",
        json={
            "username": "longpassworduser",
            "name": "Long Password User",
            "birthdate": "1994-04-04T00:00:00",
            "password": long_password,
        },
    )
    assert response.status_code == 200


def test_register_user_special_characters_in_username(test_client):
    response = test_client.post(
        "/user-register",
        json={
            "username": "user!@#$%^&*()",
            "name": "Special Char Username",
            "birthdate": "1995-05-05T00:00:00",
            "password": "Password1234",
        },
    )
    assert response.status_code == 200


def test_register_user_password_too_short(test_client):
    response = test_client.post(
        "/user-register",
        json={
            "username": "shortpwduser",
            "name": "Short Password User",
            "birthdate": "1993-03-03T00:00:00",
            "password": "short",
        },
    )
    assert response.status_code == 400
    data = response.json()
    assert "invalid password" in data["detail"]


def test_register_user_password_no_digit(test_client):
    response = test_client.post(
        "/user-register",
        json={
            "username": "nodigituser",
            "name": "No Digit User",
            "birthdate": "1994-04-04T00:00:00",
            "password": "NoDigitsHere",
        },
    )
    assert response.status_code == 400
    data = response.json()
    assert "invalid password" in data["detail"]


def test_register_user_missing_fields(test_client):
    response = test_client.post(
        "/user-register", json={"username": "incompleteuser", "name": "Incomplete User"}
    )
    assert response.status_code == 422


def test_get_user_self(test_client):
    response = test_client.post(
        "/user-register",
        json={
            "username": "selfuser",
            "name": "Self User",
            "birthdate": "1995-05-05T00:00:00",
            "password": "Password1234",
        },
    )
    assert response.status_code == 200
    user_data = response.json()
    uid = user_data["uid"]

    auth = ("selfuser", "Password1234")
    response = test_client.post(f"/user-get?id={uid}", auth=auth)
    assert response.status_code == 200
    data = response.json()
    assert data["uid"] == uid
    assert data["username"] == "selfuser"
    assert data["name"] == "Self User"


@pytest.mark.xfail(
    reason="causing UnboundLocalError cannot access local variable 'entity' where it is not associated with a value"
)
def test_get_other_user_as_normal_user(test_client):
    response = test_client.post(
        "/user-register",
        json={
            "username": "normaluser1",
            "name": "Normal User One",
            "birthdate": "1996-06-06T00:00:00",
            "password": "Password1234",
        },
    )
    assert response.status_code == 200
    user1_data = response.json()
    user1_uid = user1_data["uid"]

    response = test_client.post(
        "/user-register",
        json={
            "username": "normaluser2",
            "name": "Normal User Two",
            "birthdate": "1997-07-07T00:00:00",
            "password": "Password1234",
        },
    )
    assert response.status_code == 200
    user2_data = response.json()
    user2_uid = user2_data["uid"]

    auth = ("normaluser1", "Password1234")
    response = test_client.post(f"/user-get?id={user2_uid}", auth=auth)
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Forbidden"


def test_promote_user_as_admin(test_client):
    response = test_client.post(
        "/user-register",
        json={
            "username": "promoteuser",
            "name": "Promote User",
            "birthdate": "1999-09-09T00:00:00",
            "password": "Password1234",
        },
    )
    assert response.status_code == 200
    user_data = response.json()
    user_uid = user_data["uid"]

    auth = ("admin", "superSecretAdminPassword123")
    response = test_client.post(f"/user-promote?id={user_uid}", auth=auth)
    assert response.status_code == 200

    auth_user = ("promoteuser", "Password1234")
    response = test_client.post(f"/user-get?id={user_uid}", auth=auth_user)
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"


def test_promote_user_as_non_admin(test_client):
    response = test_client.post(
        "/user-register",
        json={
            "username": "userA",
            "name": "User A",
            "birthdate": "2000-10-10T00:00:00",
            "password": "Password1234",
        },
    )
    assert response.status_code == 200
    userA_data = response.json()
    userA_uid = userA_data["uid"]

    response = test_client.post(
        "/user-register",
        json={
            "username": "userB",
            "name": "User B",
            "birthdate": "2001-11-11T00:00:00",
            "password": "Password1234",
        },
    )
    assert response.status_code == 200
    userB_data = response.json()
    userB_uid = userB_data["uid"]

    auth = ("userA", "Password1234")
    response = test_client.post(f"/user-promote?id={userB_uid}", auth=auth)
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Forbidden"


def test_get_user_invalid_credentials(test_client):
    response = test_client.post("/user-get?id=1")
    assert response.status_code == 401

    auth = ("invaliduser", "invalidpassword")
    response = test_client.post("/user-get?id=1", auth=auth)
    assert response.status_code == 401


def test_get_user_with_both_id_and_username(test_client):
    response = test_client.post(
        "/user-register",
        json={
            "username": "bothparamsuser",
            "name": "Both Params User",
            "birthdate": "2002-12-12T00:00:00",
            "password": "Password1234",
        },
    )
    assert response.status_code == 200
    user_data = response.json()
    user_uid = user_data["uid"]

    auth = ("bothparamsuser", "Password1234")
    response = test_client.post(
        f"/user-get?id={user_uid}&username=bothparamsuser", auth=auth
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "both id and username are provided"


def test_get_user_with_neither_id_nor_username(test_client):
    response = test_client.post(
        "/user-register",
        json={
            "username": "noparamsuser",
            "name": "No Params User",
            "birthdate": "2003-01-01T00:00:00",
            "password": "Password1234",
        },
    )
    assert response.status_code == 200

    auth = ("noparamsuser", "Password1234")
    response = test_client.post("/user-get", auth=auth)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "neither id nor username are provided"


def test_promote_nonexistent_user(test_client):
    auth = ("admin", "superSecretAdminPassword123")
    response = test_client.post("/user-promote?id=9999", auth=auth)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "user not found"


def test_get_user_not_found(test_client):
    auth = ("admin", "superSecretAdminPassword123")
    response = test_client.post("/user-get?id=9999", auth=auth)
    assert response.status_code == 404


def test_user_authentication_required(test_client):
    response = test_client.post("/user-promote?id=1")
    assert response.status_code == 401


def test_value_error_handler(test_client):
    auth = ("admin", "superSecretAdminPassword123")
    response = test_client.post("/user-promote?id=not-an-integer", auth=auth)
    assert response.status_code == 422


def test_password_without_number(test_client):
    response = test_client.post(
        "/user-register",
        json={
            "username": "nonumberpassword",
            "name": "No Number Password",
            "birthdate": "2004-02-02T00:00:00",
            "password": "PasswordWithoutNumber",
        },
    )
    assert response.status_code == 400
    data = response.json()
    assert "invalid password" in data["detail"]
