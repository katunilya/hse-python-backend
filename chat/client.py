import requests
import asyncio
import websockets

chat_name = input("Enter the name of the chat room to create: ")

response = requests.post("http://localhost:8000/chat_rooms", json={"name": chat_name})
if response.status_code == 200:
    print(response.json()["message"])
else:
    print(f"Error: {response.json()['detail']}")

async def chat_client():
    uri = f"ws://localhost:8000/chat/{chat_name}"
    async with websockets.connect(uri) as websocket:
        print(f"Connected to chat room '{chat_name}'.")
        
        async def receive():
            while True:
                try:
                    response = await websocket.recv()
                    print(f"\n{response}\nYou: ", end="")
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed.")
                    break

        async def send():
            while True:
                try:
                    message = await asyncio.get_event_loop().run_in_executor(None, input, "You: ")
                    await websocket.send(message)
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed.")
                    break

        await asyncio.gather(receive(), send())

asyncio.run(chat_client())
