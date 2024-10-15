import requests

url = "http://localhost:8080/cart"

def send_request():
    response = requests.post(url)
    print(f"Status Code: {response.status_code}, Response: {response.json()}")

    response = requests.get(url)
    print(f"Status Code: {response.status_code}, Response: {response.json()}")

for _ in range(2000):
    send_request()
