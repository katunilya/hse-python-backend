from math import factorial
from typing import Any, Awaitable, Callable
from http import HTTPStatus
from pathlib import PurePath
import urllib.parse
import json

# Реализовать 'Математическое API' из примера напрямую через ASGI-compatible
# функцию. В частности
# 
# - запросы, для которых нет обработчиков (не тот метод, не тот путь) должны
#   возвращать ошибку `404 Not Found`
# - запрос `GET /factorial` (n!)
#   - возвращается в тело запроса в формате json вида `{'result': 123}`
#   - в query-параметре запроса должен быть параметр `n: int`
#   - если параметра нет, или он не является числом - возвращаем `422
#     Unprocessable Entity`
#   - если параметр не валидное число (меньше 0) - возвращаем `400 Bad Request`
# - запрос `GET /fibonacci` (n-ое число fibonacci)
#   - возвращается в тело запроса в формате json вида `{'result': 123}`
#   - в path-параметре запроса (`fibonacci/{n}`) должен быть параметр `n: int`
#   - если параметра нет, или он не является числом - возвращаем `422
#     Unprocessable Entity`
#   - если параметр не валидное число (меньше 0) - возвращаем `400 Bad Request`
# - запрос `GET /mean` (среднее массива)
#   - возвращается в тело запроса в формате json вида `{'result': 123}`
#   - в теле запроса не пустой массив из `float`'ов (например `[1, 2.3, 3.6]`)
#   - тело не является массивом `float`'ов - возвращаем `422
#     Unprocessable Entity`
#   - если массив пустой - возвращаем `400 Bad Request`


def parse_query(query_string: str) -> dict[str, str]:
    query = {
        key.decode(): [v.decode() for v in value] # type: ignore
        for key, value in urllib.parse.parse_qs(query_string).items()
    }

    return { # type: ignore
        key: value[0] if len(value) == 1 else value
        for key, value in query.items()
    }


async def send_response(
    send: Callable[[dict[str, Any]], Awaitable[None]],
    status: int | HTTPStatus,
    body: bytes,
    headers: dict[str, str] = {},
) -> None:
    await send(
        {
            'type': 'http.response.start',
            'status': status.value if isinstance(status, HTTPStatus) else status,
            'headers': [
                [key.encode(), value.encode()]
                for key, value in headers.items()
            ],
        }
    )
    await send({'type': 'http.response.body', 'body': body})


async def send_plain(
    send: Callable[[dict[str, Any]], Awaitable[None]],
    status: int | HTTPStatus,
    body: str,
    headers: dict[str, str] = {},
) -> None:
    headers |= {'content-type': 'text/plain'}
    await send_response(send, status, body.encode(), headers)

async def send_json(
    send: Callable[[dict[str, Any]], Awaitable[None]],
    status: int | HTTPStatus,
    body: dict[str, Any],
    headers: dict[str, str] = {},
) -> None:
    headers |= {'content-type': 'text/json'}
    await send_response(
        send,
        status,
        json.dumps(body, ensure_ascii=False).encode(),
        headers,
    )

async def send_status(
    send: Callable[[dict[str, Any]], Awaitable[None]],
    status: int | HTTPStatus,
    headers: dict[str, str] = {},
):
    if isinstance(status, int):
        status = HTTPStatus(status)

    await send_plain(send, status, status.phrase, headers)

async def application(
    scope: dict[str, Any],
    _: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    scope['query'] = parse_query(scope['query_string'])

    print(PurePath(scope['path']).parts[:2])
    match scope:
        case {'method': 'GET', 'path': '/factorial'}:
            n = scope['query'].get('n')
            n = int(n) if n and n.isdecimal() else None
            if n is None:
                await send_status(send, HTTPStatus.UNPROCESSABLE_ENTITY)
            elif n < 0:
                await send_status(send, HTTPStatus.BAD_REQUEST)
            else:
                await send_json(send, HTTPStatus.OK, {'result': factorial(int(n))})
        #TODO: fix
        case {'method': 'GET', 'path': path} if PurePath(path).parts[:2] == ('/', 'fibonacci'):
            path = PurePath(path)
            if not (
                len(path.parts) > 2
                and
                path.parts[2].isdecimal()
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

        case _:
            status = HTTPStatus.NOT_FOUND
            await send_plain(send, status.value, status.phrase)
