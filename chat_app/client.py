import requests
import asyncio
import websockets
import sys


async def chat_client():
    while True:
        chat_name = input("Enter the name of the chat room: ")

        choice = input(
            "Do you want to (1) Create a new chat room or (2) Join an existing one? Enter 1 or 2: "
        )

        if choice == "1":
            response = requests.post(
                "http://localhost:8000/chat_rooms", json={"name": chat_name}
            )
            if response.status_code == 200:
                print(response.json()["message"])
            elif response.status_code == 400:
                print(
                    f"Chat room '{chat_name}' already exists. Cannot create it again."
                )
                join_existing = input(
                    "Do you want to join the existing chat room? (y/n): "
                )
                if join_existing.lower() == "y":
                    break
                else:
                    continue
            else:
                print(f"Error: {response.json()['detail']}")
                sys.exit(1)
        elif choice == "2":
            response = requests.get("http://localhost:8000/chat_rooms")
            if response.status_code == 200:
                chat_rooms = response.json().get("chat_rooms", [])
                if chat_name not in chat_rooms:
                    print(f"Chat room '{chat_name}' does not exist.")
                    create_room = input("Do you want to create it? (y/n): ")
                    if create_room.lower() == "y":
                        response = requests.post(
                            "http://localhost:8000/chat_rooms", json={"name": chat_name}
                        )
                        if response.status_code == 200:
                            print(response.json()["message"])
                            break
                        else:
                            print(f"Error: {response.json()['detail']}")
                            continue
                    else:
                        continue
                else:
                    print(f"Joining chat room '{chat_name}'.")
                    break
            else:
                print(f"Error: {response.json()['detail']}")
                sys.exit(1)
        else:
            print("Invalid choice. Please enter 1 or 2.")
            continue

    username = input("Enter your username: ")

    uri = f"ws://localhost:8000/chat/{chat_name}"
    async with websockets.connect(uri) as websocket:
        await websocket.send(f"/username {username}")

        print(f"Connected to chat room '{chat_name}' as '{username}'.")

        async def receive():
            while True:
                try:
                    response = await websocket.recv()
                    print(f"\r{response}\nYou: ", end="")
                except websockets.exceptions.ConnectionClosed:
                    print("\nConnection closed.")
                    break

        async def send():
            while True:
                try:
                    message = await asyncio.get_event_loop().run_in_executor(
                        None, input, "You: "
                    )
                    await websocket.send(message)
                except websockets.exceptions.ConnectionClosed:
                    print("\nConnection closed.")
                    break

        await asyncio.gather(receive(), send())


asyncio.run(chat_client())
