from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from faker import Faker

faker = Faker()

# Функция для создания товара (аналог создания "пользователей")
def create_items():
    for _ in range(500):
        item = {
            "name": faker.word(),  # Генерация случайного названия товара
            "price": faker.random_number(digits=2)  # Генерация случайной цены
        }
        response = requests.post(
            "http://localhost:8080/item",
            json=item
        )

        # Выводим статус ответа и текст для отладки
        print(response.status_code, response.text)

# Функция для получения товаров (по случайным ID)
def get_items():
    for _ in range(500):
        item_id = faker.random_number(digits=2)  # Генерация случайного ID товара
        response = requests.get(
            f"http://localhost:8080/item/{item_id}"
        )

        # Выводим статус ответа и текст для отладки
        print(response.status_code, response.text)

# Параллельное выполнение запросов
with ThreadPoolExecutor() as executor:
    futures = {}

    # Параллельное создание товаров
    for i in range(15):
        futures[executor.submit(create_items)] = f"create-item-{i}"

    # Параллельное получение товаров
    for i in range(15):
        futures[executor.submit(get_items)] = f"get-item-{i}"

    # Отслеживание завершения задач
    for future in as_completed(futures):
        print(f"completed {futures[future]}")
