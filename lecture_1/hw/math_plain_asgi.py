import statistics
import json
import http
import math

from typing import Any, Awaitable, Callable

from urllib.parse import parse_qs, urlparse
from typing import Dict

SendCallableType = Callable[[http.HTTPStatus, str], Awaitable[Any]]

class Endpoint:
    def __init__(self, path: str, method: http.HTTPMethod):
        self.path = path
        self.method = method

    def match(self, scope: dict[str, Any]) -> bool:
        """
        Проверяет может ли данный endpoint обработать запрос
        """
        pass

    async def handle(
        self, 
        scope: dict[str, Any], 
        receive: Callable[[], Awaitable[dict[str, Any]]], 
        send: Callable[[dict[str, Any]], Awaitable[None]],
    ):
        """
        Обрабатывает запрос и отправляет ответ
        """
        pass

def parse_query_string(query_string: str) -> Dict[str, str]:
    parsed_params = parse_qs(query_string)
    return {key: values[0] for key, values in parsed_params.items()}


async def send_response(send, status_code: http.HTTPStatus, body: Dict):
    response_body = json.dumps(body).encode('utf-8')
    headers = [
        (b'content-type', b'application/json'),
        (b'content-length', str(len(response_body)).encode('utf-8'))
    ]
    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': headers
    })
    await send({
        'type': 'http.response.body',
        'body': response_body,
    })

async def read_body(receive):
    """
    Read and return the entire body from an incoming ASGI message.
    """
    body = b''
    more_body = True

    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)

    return body

class MeanEndpoint(Endpoint):
    def __init__(self):
        super().__init__(path="/mean", method=http.HTTPMethod.GET)

    def match(self, scope: dict[str, Any]) -> bool:
        return scope['method'] == self.method.value and scope['path'] == self.path
    
    def _is_array_of_numbers(data):
        if not isinstance(data, list):
            return False
        return all(isinstance(item, (int, float)) for item in data)

    async def handle(self, scope, receive, send):
        try:
            body = await read_body(receive)
            if not body:
                await send_response(send, http.HTTPStatus.UNPROCESSABLE_ENTITY, {"error" : "Empty or invalid data"})
                return
            
            data = json.loads(body)
            if not data or not MeanEndpoint._is_array_of_numbers(data):
                await send_response(send, http.HTTPStatus.BAD_REQUEST, {"error" : "Empty or invalid data"})
            else:
                await send_response(send, http.HTTPStatus.OK, {"result": (statistics.mean(data))})
        except ValueError:
                await send_response(send, http.HTTPStatus.UNPROCESSABLE_ENTITY, {"error" : "Not data"})



class FactorialEndpoint(Endpoint):
    def __init__(self):
        self.query_param_name = 'n'
        super().__init__(path="/factorial", method=http.HTTPMethod.GET)

    def match(self, scope: dict[str, Any]) -> bool:
        return scope['method'] == self.method.value and scope['path'] == self.path

    async def handle(self, scope, receive, send):
        query_string = scope['query_string'].decode('utf-8')
        query_params = parse_query_string(query_string)
        param = query_params.get(self.query_param_name, None)

        if not param:
            await send_response(send, http.HTTPStatus.UNPROCESSABLE_ENTITY, {"error" : "Empty"})
        else:
            try:
                param = int(param)
                if param < 0:
                    await send_response(send, http.HTTPStatus.BAD_REQUEST, {"error" : "It's a negative number"})
                else:
                    await send_response(send, http.HTTPStatus.OK, {"result": math.factorial(param)})
            except ValueError:
                await send_response(send, http.HTTPStatus.UNPROCESSABLE_ENTITY, {"error" : "Not a number"})


class FibonacciEndpoint(Endpoint):
    def __init__(self):
        super().__init__(path="/fibonacci", method=http.HTTPMethod.GET)

    def fib(n: int):
        if n == 0:
            return 0
        elif n == 1 or n == 2:
            return 1
        else:
            return FibonacciEndpoint.fib(n-1) + FibonacciEndpoint.fib(n-2)

    def match(self, scope) -> bool:
        path = urlparse(scope['path'])[2]
        return scope["method"] == self.method.value and path.startswith(self.path)

    async def handle(self, scope, receive, send):
        url_parts = urlparse(scope['path'])
        param = url_parts[2].rsplit('/', 1)[-1]

        if not param:
            await send_response(send, http.HTTPStatus.UNPROCESSABLE_ENTITY, {"error" : "Not a number"})
        else:
            try:
                if int(param) < 0:
                    await send_response(send, http.HTTPStatus.BAD_REQUEST, {"error" : "It's a negative number"})
                else:
                    await send_response(send, http.HTTPStatus.OK, {"result": FibonacciEndpoint.fib(int(param))})
            except ValueError:
                await send_response(send, http.HTTPStatus.UNPROCESSABLE_ENTITY, {"error" : "Not a number"})


async def app(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None: 
    assert scope['type'] == 'http'
    endpoints = [MeanEndpoint(), FactorialEndpoint(), FibonacciEndpoint()]

    if any(map(lambda e: e.match(scope), endpoints)):
        for endpoint in endpoints:
            if endpoint.match(scope):
                await endpoint.handle(scope, receive, send)
    else:
        await send_response(send, http.HTTPStatus.NOT_FOUND, {"error": "Endpoint not found"})
    
