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
    status: int,
    headers: dict[str, str],
    body: bytes
) -> None:
    await send(
        {
            'type': 'http.response.start',
            'status': status,
            'headers': [
                [key.encode(), value.encode()]
                for key, value in headers.items()
            ],
        }
    )
    await send({'type': 'http.response.body', 'body': body})



async def send_plain(
    send: Callable[[dict[str, Any]], Awaitable[None]],
    status: int,
    headers: dict[str, str],
    body: str
) -> None:
    headers |= {'content-type': 'text/plain'}
    await send_response(send, status, headers, body.encode())

async def send_json(
    send: Callable[[dict[str, Any]], Awaitable[None]],
    status: int,
    headers: dict[str, str],
    body: dict[str, Any],
) -> None:
    headers |= {'content-type': 'text/json'}
    await send_response(
        send, status, headers,
        json.dumps(body, ensure_ascii=False).encode()
    )


async def application(
    scope: dict[str, Any],
    _: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    scope['query'] = parse_query(scope['query_string'])

    match scope:
        case {'method': 'GET', 'path': '/factorial'}:
            n = scope['query'].get('n')

            n = int(n) if n and n.isdecimal() else None

            if n is None:
                status = HTTPStatus.UNPROCESSABLE_ENTITY
                await send_plain(send, status.value, {}, status.phrase)
            elif n < 0:
                status = HTTPStatus.BAD_REQUEST
                await send_plain(send, status.value, {}, status.phrase)
            else:
                status = HTTPStatus.OK
                await send_json(send, status.value, {}, {'result': factorial(int(n))})
        case _:
            status = HTTPStatus.NOT_FOUND
            await send_plain(send, status.value, {}, status.phrase)
