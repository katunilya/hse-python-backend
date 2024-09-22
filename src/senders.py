# Функция для отправки JSON ответа
from http import HTTPStatus
import json


async def send_response(send, data: dict):
    await send({
        "type": "http.response.start",
        "status": HTTPStatus.OK,
        "headers": [[b"content-type", b"application/json"]]
    })
    await send({"type": "http.response.body", "body": json.dumps(data).encode()})

async def send_400(send, detail: str):
    await send({
        "type": "http.response.start",
        "status": HTTPStatus.BAD_REQUEST,
        "headers": [[b"content-type", b"application/json"]]
    })
    await send({"type": "http.response.body", "body": json.dumps({"detail": detail}).encode()})

async def send_422(send):
    await send({
        "type": "http.response.start",
        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
        "headers": [[b"content-type", b"application/json"]]
    })
    await send({"type": "http.response.body", "body": b'{"detail": "Unprocessable Entity"}'})
