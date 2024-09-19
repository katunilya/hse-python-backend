import json
from http import HTTPStatus

from exceptiongroup import catch

from client import send_data
from service import get_factorial, get_fibonacci, get_mean

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

async def app(scope, receive, send) -> None:

    if scope['method'] != 'GET':
        await send_data(send, HTTPStatus.NOT_FOUND, {"error" : "Not Found"})

    try:
        if scope['path'] == '/factorial':
            try:
                l = scope['query_string'].decode('utf-8').split("&")
                d = dict([cur.split("=") for cur in l])
                n = int(d["n"])
            except Exception:
                await send_data(send, HTTPStatus.UNPROCESSABLE_ENTITY, {"error" : "Not a number"})
                return

            await send_data(send, HTTPStatus.OK, {"result": get_factorial(n)})
        elif scope['path'].startswith('/fibonacci'):
            try:
                data = scope['path'].split("/")[-1]
                data = int(data)
            except Exception:
                await send_data(send, HTTPStatus.UNPROCESSABLE_ENTITY, {"error" : "Not a number"})
                return

            await send_data(send, HTTPStatus.OK, {"result": get_fibonacci(data)})
        elif scope['path'] == '/mean':
            try:
                data = json.loads(await read_body(receive))
                data = list(data)
            except Exception:
                await send_data(send, HTTPStatus.UNPROCESSABLE_ENTITY, {"error" : "Not a number"})
                return

            await send_data(send, HTTPStatus.OK, {"result": get_mean(data)})
        else:
            await send_data(send, HTTPStatus.NOT_FOUND, {"error": "Not Found"})
    except Exception:
        await send_data(send, HTTPStatus.BAD_REQUEST, "Bad Request")
