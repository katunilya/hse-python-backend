import asyncio
import socket
import http

from endpoint import Endpoint
from app import MeanEndpoint, FactorialEndpoint, FibonacciEndpoint

from typing import List, Dict

class AsyncServer:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.server_socket = None
        self._endpoints: List[Endpoint] = []
        self._is_running = False


    def add_endpoint(self, point: Endpoint):
        """
        Добавляем новую точку входа на сервере
        :param point: объект запроса
        """
        self._endpoints.append(point)


    def _create_response(self, code: http.HTTPStatus, body: str) -> str:
        response = f"HTTP/1.1 {code.value} {code.phrase}\r\n"
        response += "Content-Type: text/plain\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += "Connection: close\r\n\r\n"
        response += body
        return response
    

    def _parse_request(request_string: str) -> Dict[str, str]:
        splitted_request = request_string.split('\r\n')
        scope = dict()
        scope['method'], scope['path'], scope['version'] = splitted_request[0].split(' ')
        scope['data'] = splitted_request[-1]
        return scope


    async def _handle_client(self, client_socket):
        loop = asyncio.get_running_loop()
        addr = client_socket.getpeername()

        print(f"Connected with {addr}")

        data = await loop.sock_recv(client_socket, 1024)
        request = AsyncServer._parse_request(data.decode('utf-8'))
        print(f"Received {request} from {addr}")

        async def send(code: http.HTTPStatus, body: str):
            response = self._create_response(code, body).encode('utf-8')
            await loop.sock_sendall(client_socket, response)
            client_socket.close()

        for endpoint in self._endpoints:
            if endpoint.match(request):
                await endpoint.handle(request, send)
                print(f"Connection closed with {addr}")
                return
            
        await send(http.HTTPStatus.NOT_FOUND, "404 Not Found")
        print(f"Connection closed with {addr}")


    async def start(self):
        if self._is_running:
            print("Server has already started")
            return

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.setblocking(False)
        self.server_socket.listen(5)
        self._is_running = True

        print(f"Server is listening on {self.host}:{self.port}...")

        loop = asyncio.get_event_loop()
        while True:
            client, _ = await loop.sock_accept(self.server_socket)
            loop.create_task(self._handle_client(client))


    def close(self):
        if self._is_running:
            self._is_running = False
            self.server_socket.close()
            print("Server closed")
        else:
            print("Server has already stoped")
    

if __name__ == "__main__":
    try:
        server = AsyncServer(port=8000)
        server.add_endpoint(MeanEndpoint())
        server.add_endpoint(FibonacciEndpoint())
        server.add_endpoint(FactorialEndpoint())
        asyncio.run(server.start())
    except KeyboardInterrupt:
        server.close()
