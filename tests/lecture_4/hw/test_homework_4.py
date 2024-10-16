import base64
from http import HTTPStatus
import pytest
from faker import Faker
from fastapi.testclient import TestClient

from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.core.users import *

faker = Faker()

@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client

user_data_test = [
    (
        {
            "username": "my_user",
            "name": "Igor",
            "birthdate": "1995-05-10T00:00:00",
            "password": "longlongpas123"
        },
        200
    ),
        (
        {
            "username": "my_user2",
            "name": "Igor2",
            "birthdate": "1996-05-10T00:00:00",
            "password": "incpas"
        },
        400
    )
]

@pytest.mark.parametrize("user_data, status", user_data_test)
def test_reg_user(client, user_data, status):
    response = client.post("/user-register", json=user_data)
    assert status == response.status_code
    responce_data = response.json()
    if status == 200:
        responce_data["username"] == user_data["username"]
        responce_data["name"] == user_data["name"]
        responce_data["birthdate"] == user_data["birthdate"]
        #responce_data["password"] == user_data["password"]
        
data_test = [
    (
        {
            "username": "my_user",
            "name": "Igor",
            "birthdate": "1995-05-10",
            "password": "longlongpasss123"
        },
        200
    )
]        
@pytest.mark.parametrize("data_test, status", data_test)        
def test_promote_and_get_user(client, data_test, status):
    response = client.post("/user-register", json=data_test)
    assert response.status_code == status
    response_data = response.json()
    user_id = response_data["uid"]
    
    admin_psw = "admin:superSecretAdminPassword123"
    admin_encr = admin_psw.encode("utf-8")
    base64_encr_to_server = base64.b64encode(admin_encr).decode("utf-8")
    header =  {
        "Authorization": f"Basic {base64_encr_to_server}"
    }
    
    get_admin = client.post(f"/user-get?username=admin", headers=header)
    assert 200 == get_admin.status_code
    assert UserRole.ADMIN == get_admin.json()["role"]
    
    get_data = client.post(f"/user-promote?id={user_id}", headers=header)
    assert 200 == get_data.status_code
    if get_data.status_code == 200:
        promoted_user = client.post(f"/user-get?id={user_id}", headers=header) 
        promoted_data = promoted_user.json()
        assert promoted_data["role"] == UserRole.ADMIN.value
        
#возможно, можно было бы повыносить код, но здесь рассматриваются крайние случаи, в которых часто требуются разные данные
@pytest.mark.parametrize("data_test, status", data_test)      
def test_check_invalid_data(client, data_test, status):
    admin_psw = "admin:superSecretAdminPassword123"
    admin_encr = admin_psw.encode("utf-8")
    base64_encr_to_server = base64.b64encode(admin_encr).decode("utf-8")
    header =  {
        "Authorization": f"Basic {base64_encr_to_server}"
    }
    # Тест 1: Запрос без id и username 
    get_invalid_data = client.post(f"/user-get", headers=header)
    assert get_invalid_data.status_code == 400 
    response_data = get_invalid_data.json()
    assert "neither id nor username are provided" in response_data["detail"]
    
    register_regular_user = client.post("/user-register", json=data_test)
    assert status == register_regular_user.status_code
    user_id = register_regular_user.json()["uid"]
    
    # Тест 2: Запрос c id и username 
    name_and_id = client.post(f"/user-get?id={user_id}&username=my_user", headers=header)
    assert name_and_id.status_code == 400 
    assert "both id and username are provided" in name_and_id.json()["detail"]
    
    # Тест 3: некорректный id 
    invalid_id = user_id + 1000 
    get_invalid_user = client.post(f"/user-get?id={invalid_id}", headers=header)
    assert get_invalid_user.status_code == 404
    response_data = get_invalid_user.json()
    assert "Not Found" in response_data["detail"]
    
    # Тест 4: некорректный пароль у существующего пользователя 
    wrong_header = {
        "Authorization": f"Basic {base64.b64encode(b'my_user:wrong_pass123').decode('utf-8')}"
    }
    unauthorized_response = client.post(f"/user-get?id={user_id}", headers=wrong_header)
    assert unauthorized_response.status_code == HTTPStatus.UNAUTHORIZED
    
    # Тест 5: повышаем пользователя не от имени администратора
    not_admin_header = {
        "Authorization": f"Basic {base64.b64encode(b'my_user:longlongpasss123').decode('utf-8')}"
    }
    not_admin = client.post(f"/user-promote?id={user_id}", headers=not_admin_header)
    assert not_admin.status_code == HTTPStatus.FORBIDDEN
    
    # Тест 6: повышаем не существующего пользователя
    non_exist_user = client.post(f"/user-promote?id={invalid_id}", headers=header)
    assert non_exist_user.status_code == HTTPStatus.BAD_REQUEST
    
    # Тест 7: регистрируем зарегистрированного пользователя
    response_duplicate_user = client.post("/user-register", json=data_test)
    assert response_duplicate_user.status_code == 400
    assert "username is already taken" in response_duplicate_user.json()["detail"]
    
    # Тест 8: некорректный пароль
    invalid_password_data = {
        "username": "new_new_user",
        "name": "Test User",
        "birthdate": "1995-05-10",
        "password": "short" 
    }
    response_invalid_password = client.post("/user-register", json=invalid_password_data)
    assert response_invalid_password.status_code == 400
    assert "invalid password" in response_invalid_password.json()["detail"]
    
    # Тест 9: Проверка метода get_by_username
    non_existent_user_response = client.post(f"/user-get?username=non_existent_user", headers=header)
    assert non_existent_user_response.status_code == HTTPStatus.NOT_FOUND