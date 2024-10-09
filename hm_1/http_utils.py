from typing import Callable, Dict, Any
import json


async def http_error(code: int, message: str, send: Callable[[Dict[str, Any]], Any]):
    await send(
        {
            "type": "http.response.start",
            "status": code,
            "headers": [[b"content-type", b"text/plain"]],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": bytes(message, encoding="utf-8"),
        }
    )


async def send_result(result, send: Callable[[Dict[str, Any]], Any]):
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [[b"content-type", b"text/plain"]],
        }
    )
    await send(
        {"type": "http.response.body", "body": json.dumps({"result": result}).encode("utf-8")}
    )
