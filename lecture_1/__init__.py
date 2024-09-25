import json
from math import factorial
from typing import Any, Awaitable, Callable
from http import HTTPStatus
from pathlib import PurePath
from .validators import is_number, str_is_int
from .utils import parse_query
from .responses import send_status, send_json

async def application(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    scope['query'] = parse_query(scope['query_string'])
    match scope:
        case {'method': 'GET', 'path': '/factorial'}:
            n = scope['query'].get('n')
            n = ( 
                int(n)
                if n and str_is_int(n) 
                else None
            ) 
            if n is None:
                await send_status(send, HTTPStatus.UNPROCESSABLE_ENTITY)
            elif n < 0:
                await send_status(send, HTTPStatus.BAD_REQUEST)
            else:
                await send_json(send, HTTPStatus.OK, {'result': factorial(int(n))})

        case {'method': 'GET', 'path': path} if PurePath(path).parts[:2] == ('/', 'fibonacci'):
            path = PurePath(path)
            if not (
                len(path.parts) > 2 and str_is_int(path.parts[2])
            ):
                await send_status(send, HTTPStatus.UNPROCESSABLE_ENTITY)
            elif int(path.parts[2]) < 0:
                await send_status(send, HTTPStatus.BAD_REQUEST)
            else:
                n = int(path.parts[2])
                a, b = 0, 1
                for i in range(n):
                    a, b = b, a + b
                await send_json(send, HTTPStatus.OK, {'result': b})

        case {'method': 'GET', 'path': '/mean'}:
            recv = await receive()
            body = recv['body']
            while (recv.get('more_body')):
                recv = await receive()
                body += recv['body']

            try:
                lst = json.loads(body)
                if lst == []:
                    await send_status(send, HTTPStatus.BAD_REQUEST)
                elif isinstance(lst, list) and all(map(is_number, lst)):
                    await send_json(
                        send, HTTPStatus.OK, {'result': sum(lst) / len(lst)}
                    )
                else:
                    await send_status(send, HTTPStatus.UNPROCESSABLE_ENTITY)
            except json.JSONDecodeError:
                await send_status(send, HTTPStatus.UNPROCESSABLE_ENTITY)

        case _:
            await send_status(send, HTTPStatus.NOT_FOUND)
