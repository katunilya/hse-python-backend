import json
from http import HTTPStatus
from typing import Callable, Any, Awaitable

from . import client
from . import service

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

async def app(scope, receive, send):
    try:
        if scope['type'] != 'http':
            await client.send_data(send, HTTPStatus.NOT_FOUND, {"error": "Not Found"})
            return
        if scope['path'] == '/factorial':
            try:
                l = scope['query_string'].decode('utf-8').split("&")
                d = dict([cur.split("=") for cur in l])
                n = int(d["n"])
            except Exception:
                await client.send_data(send, HTTPStatus.UNPROCESSABLE_ENTITY, {"error" : "Not a number"})
                return

            await client.send_data(send, HTTPStatus.OK, {"result": service.get_factorial(n)})
        elif scope['path'].startswith('/fibonacci'):
            try:
                data = scope['path'].split("/")[-1]
                data = int(data)
            except Exception:
                await client.send_data(send, HTTPStatus.UNPROCESSABLE_ENTITY, {"error" : "Not a number"})
                return

            await client.send_data(send, HTTPStatus.OK, {"result": service.get_fibonacci(data)})
        elif scope['path'] == '/mean':
            try:
                data = json.loads(await read_body(receive))
                data = list(data)
            except Exception:
                await client.send_data(send, HTTPStatus.UNPROCESSABLE_ENTITY, {"error" : "Not a number"})
                return

            await client.send_data(send, HTTPStatus.OK, {"result": service.get_mean(data)})
        else:
            await client.send_data(send, HTTPStatus.NOT_FOUND, {"error": "Not Found"})
    except Exception:
        await client.send_data(send, HTTPStatus.BAD_REQUEST, "Bad Request")
