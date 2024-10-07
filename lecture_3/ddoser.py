from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from faker import Faker

faker = Faker()


def create_users():
    for _ in range(500):
        user = faker.profile()
        response = requests.post(
            "http://localhost:8080/cart",

        )

        print(response)


def get_users():
    for i in range(500):
        
        response = requests.get(
            f"http://localhost:8080/1",
            # params={"id": faker.random_number(digits=2)},
        )
        print(response)


with ThreadPoolExecutor() as executor:
    futures = {}

    for i in range(15):
        futures[executor.submit(create_users)] = f"create-user-{i}"

    for _ in range(15):
        futures[executor.submit(get_users)] = f"get-users-{i}"

    for future in as_completed(futures):
        print(f"completed {futures[future]}")
