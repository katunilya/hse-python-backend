import json
from http import HTTPStatus
from typing import Any, Awaitable, Callable

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
