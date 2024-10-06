from typing import Any, Awaitable, Callable
import math
import urllib.parse
import json
import numpy as np


async def send_start(send, status, headers):
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": headers,
    })


async def send_body(send, body):
    await send({
        "type": "http.response.body",
        "body": body,
    })


async def send_not_found(send):
    await send_start(send, 404, [[b"content-type", b"text/plain"]])
    await send_body(send, b'Not found')


async def factorial(query_string, send):
    query_params = urllib.parse.parse_qs(query_string.decode('utf-8'))
    n_str = query_params.get('n', [''])[0]

    if n_str == '' or (n_str[0] == '-' and not n_str[1:].isdigit()) or (n_str[0] != '-' and not n_str.isdigit()):
        await send_start(send, 422, [[b"content-type", b"text/plain"]])
        await send_body(send, b'Unprocessable Entity')
        return None

    if int(n_str) < 0:
        await send_start(send, 400, [[b"content-type", b"text/plain"]])
        await send_body(send, b'Bad Request')
        return None

    n = int(n_str)
    n_fact = math.factorial(n)
    response_body = json.dumps({"result": n_fact})
    body_bytes = response_body.encode('utf-8')

    await send_start(send, 200, [[b"content-type", b"application/json"]])
    await send_body(send, body_bytes)


def get_fibonacci_num(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


async def fibonacci(path, send):
    path_parts = path.split('/')

    if len(path_parts) != 3 or (path_parts[2][0] == '-' and not path_parts[2][1:].isdigit()) or (
            path_parts[2][0] != '-' and not path_parts[2].isdigit()):
        await send_start(send, 422, [[b"content-type", b"text/plain"]])
        await send_body(send, b'Unprocessable Entity')
        return None

    if int(path_parts[2]) < 0:
        await send_start(send, 400, [[b"content-type", b"text/plain"]])
        await send_body(send, b'Bad Request')
        return None

    n = int(path_parts[2])
    n_fib = get_fibonacci_num(n)
    response_body = json.dumps({"result": n_fib})
    body_bytes = response_body.encode('utf-8')

    await send_start(send, 200, [[b"content-type", b"application/json"]])
    await send_body(send, body_bytes)


async def get_mean(send, receive):
    decoded_string = receive.get("body").decode('utf-8')
    if not decoded_string:
        await send_start(send, 422, [[b"content-type", b"text/plain"]])
        await send_body(send, b'Unprocessable Entity')
        return None
    if decoded_string == '[]':
        await send_start(send, 400, [[b"content-type", b"text/plain"]])
        await send_body(send, b'Bad Request')
        return None
    try:
        decoded_list = [float(el) for el in decoded_string[1:-1].split(',')]
        response_body = json.dumps({"result": np.mean(decoded_list)})
        body_bytes = response_body.encode('utf-8')
        await send_start(send, 200, [[b"content-type", b"application/json"]])
        await send_body(send, body_bytes)
    except:
        await send_start(send, 422, [[b"content-type", b"text/plain"]])
        await send_body(send, b'Unprocessable Entity')
        return None


async def app(
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]]
) -> None:
    if scope['type'] == 'lifespan':
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                await send({'type': 'lifespan.shutdown.complete'})
                return
    elif scope['type'] == 'http':
        path = scope['path']
        method = scope.get("method", "GET")
        if method == 'GET':
            if path == '/factorial':
                await factorial(scope['query_string'], send)
            elif path == '/mean':
                await get_mean(send, await receive())
            elif path.startswith('/fibonacci'):
                await fibonacci(path, send)
            else:
                await send_not_found(send)
        else:
            await send_not_found(send)
