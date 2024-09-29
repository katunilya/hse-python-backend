from http import HTTPStatus
from typing import Any, Callable, Awaitable


class BaseHandler:
    def __init__(self, scope: dict[str, Any],
                 receive: Callable[[], Awaitable[dict[str, Any]]],
                 send: Callable[[dict[str, Any]], Awaitable[None]]):
        self.scope = scope
        self.receive = receive
        self.send = send

    async def send_result(self, result):
        await send_response(self.send, 200, f'{{"result": {result}}}'.encode())

    async def send_422(self):
        await Errors.send_422(self.send)

    async def send_404(self):
        await Errors.send_404(self.send)

    async def send_400(self):
        await Errors.send_400(self.send)

    async def body(self):
        res = []
        more_body = True
        while more_body:
            received = await self.receive()
            res.append(received['body'])
            more_body = received.get('more_body', False)
        return b''.join(res)


class Errors:
    @staticmethod
    async def send_422(send):
        await send_response(send, HTTPStatus.UNPROCESSABLE_ENTITY, b'422 Unprocessable Entity')

    @staticmethod
    async def send_404(send):
        await send_response(send, HTTPStatus.NOT_FOUND, b'404 Not Found')

    @staticmethod
    async def send_400(send):
        await send_response(send, HTTPStatus.BAD_REQUEST, b'400 Bad Request')


async def send_response(send, status, body):
    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [
            (b'content-type', b'text/plain'),
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': body,
    })


def is_int(s: str):
    return s.isdigit() or len(s) > 0 and s[0] == '-' and s[1:].isdigit()
