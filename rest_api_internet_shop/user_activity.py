import requests
import threading
import time
from random import randint, choice

BASE_URL = "http://localhost:8000" 

def create_item(name: str, price: float):
    url = f"{BASE_URL}/item/"
    payload = {"name": name, "price": price}
    response = requests.post(url, json=payload)
    return response.json()

def get_item(item_id: int):
    url = f"{BASE_URL}/item/{item_id}"
    response = requests.get(url)
    return response.json()

def get_items():
    url = f"{BASE_URL}/item/"
    response = requests.get(url)
    return response.json()

def replace_item(item_id: int, name: str, price: float):
    url = f"{BASE_URL}/item/{item_id}"
    payload = {"name": name, "price": price}
    response = requests.put(url, json=payload)
    return response.json()

def update_item(item_id: int, name: str = None, price: float = None):
    url = f"{BASE_URL}/item/{item_id}"
    payload = {}
    if name is not None:
        payload["name"] = name
    if price is not None:
        payload["price"] = price
    response = requests.patch(url, json=payload)
    return response.json()

def delete_item(item_id: int):
    url = f"{BASE_URL}/item/{item_id}"
    response = requests.delete(url)
    return response.json()

def create_cart():
    url = f"{BASE_URL}/cart/"
    response = requests.post(url)
    return response.json()

def get_cart(cart_id: int):
    url = f"{BASE_URL}/cart/{cart_id}"
    response = requests.get(url)
    return response.json()

def add_item_to_cart(cart_id: int, item_id: int):
    url = f"{BASE_URL}/cart/{cart_id}/add/{item_id}"
    response = requests.post(url)
    return response.json()

def simulate_user_behavior(item_ids):
    cart = create_cart()
    cart_id = cart["id"]

    for _ in range(randint(1, 5)):
        item_id = choice(item_ids)
        add_item_to_cart(cart_id, item_id)

    
    cart_details = get_cart(cart_id)
    print(f"Cart {cart_id} details: {cart_details}")

def main():
    item_ids = []
    for i in range(1, 11):
        name = f"Item {i}"
        price = round(randint(100, 1000) * 0.1, 2)
        item = create_item(name, price)
        item_ids.append(item["id"])

    threads = []
    for _ in range(500):  
        t = threading.Thread(target=simulate_user_behavior, args=(item_ids,))
        threads.append(t)
        t.start()
        time.sleep(0.1)  

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
