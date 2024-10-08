from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from faker import Faker

faker = Faker()


def create_cart():
    response = requests.post(
        "http://localhost:8080/cart",
    )
    print(response)
    return response.json()["id"]

def get_cart(id):
    response = requests.get(
        f"http://localhost:8080/cart/{id}",
    )
    print(response)
    return response.json()

def get_carts_list(
    offset: int = 0,
    limit: int = 10,
    min_price: float | None = None,
    max_price: float | None = None,
    min_quantity: int | None = None,
    max_quantity: int | None = None,
):
    params = {
        "offset": offset,
        "limit": limit,
    }
    if min_price is not None:
        params["min_price"] = min_price
    if max_price is not None:
        params["max_price"] = max_price
    if min_quantity is not None:
        params["min_quantity"] = min_quantity
    if max_quantity is not None:
        params["max_quantity"] = max_quantity

    response = requests.get(
        "http://localhost:8080/cart",
        params=params,
    )
    print(response)
    return response.json()

def add_item_to_cart(cart_id, item_id):
    response = requests.post(
        f"http://localhost:8080/cart/{cart_id}/add/{item_id}",
    )
    print(response)

def main():
    with ThreadPoolExecutor() as executor:
        futures = {}

        for i in range(15):
            futures[executor.submit(create_cart)] = f"create-cart-{i}"

        for i in range(15):
            futures[executor.submit(get_cart, i)] = f"get-cart-{i}"

        for i in range(15):
            futures[executor.submit(add_item_to_cart, i, 1)] = f"add-item-to-cart-{i}"

        for i in range(15):
            futures[executor.submit(get_carts_list)] = f"get-carts-list-{i}"

        for future in as_completed(futures):
            print(f"completed {futures[future]}")

if __name__ == "__main__":
    main()