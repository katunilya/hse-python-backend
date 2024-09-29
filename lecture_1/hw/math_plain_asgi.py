from typing import Any, Awaitable, Callable

import json
import math
from urllib.parse import parse_qs


async def send_response(send, status, body, content_type="application/json"):
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                [b"content-type", content_type.encode()],
            ],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": body,
        }
    )


async def send_error(send, status, message):
    await send_response(send, status, message.encode(), content_type="text/plain")


def exception_handler(func):
    async def wrapper(scope, receive, send):
        try:
            await func(scope, receive, send)
        except ValueError:
            await send_error(send, 422, "422 Unprocessable Entity")
        except Exception:
            await send_error(send, 500, "500 Internal Server Error")

    return wrapper


# '/factorial?n=...'
@exception_handler
async def handle_factorial(scope, receive, send):
    query_string = scope.get("query_string", b"").decode()
    query_params = parse_qs(query_string)
    n_values = query_params.get("n", [])
    if not n_values:
        raise ValueError("Missing parameter n")
    n_str = n_values[0]
    n = int(n_str)
    if n < 0:
        await send_error(send, 400, "400 Bad Request")
        return
    result = math.factorial(n)
    response_body = json.dumps({"result": result}).encode()
    await send_response(send, 200, response_body)


# '/fibonacci/...'
@exception_handler
async def handle_fibonacci(scope, receive, send):
    path = scope["path"]
    parts = path.split("/")
    if len(parts) != 3 or not parts[2]:
        raise ValueError("Invalid path parameter")
    n_str = parts[2]
    n = int(n_str)
    if n < 0:
        await send_error(send, 400, "400 Bad Request")
        return

    def fib(n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    result = fib(n)
    response_body = json.dumps({"result": result}).encode()
    await send_response(send, 200, response_body)


# '/mean + body (array)'
@exception_handler
async def handle_mean(scope, receive, send):
    body = b""
    more_body = True
    while more_body:
        event = await receive()
        if event["type"] == "http.request":
            body += event.get("body", b"")
            more_body = event.get("more_body", False)
        else:
            break
    array = json.loads(body.decode())
    if not isinstance(array, list):
        raise ValueError("Body must be an array")
    if not array:
        await send_error(send, 400, "400 Bad Request")
        return
    if not all(isinstance(item, (int, float)) for item in array):
        raise ValueError("Array must contain numbers")
    mean_value = sum(array) / len(array)
    response_body = json.dumps({"result": mean_value}).encode()
    await send_response(send, 200, response_body)


async def app(
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    if scope["type"] != "http":
        return

    method = scope["method"]
    path = scope["path"]

    if method == "GET" and path == "/factorial":
        await handle_factorial(scope, receive, send)
    elif method == "GET" and path.startswith("/fibonacci/"):
        await handle_fibonacci(scope, receive, send)
    elif method == "GET" and path == "/mean":
        await handle_mean(scope, receive, send)
    else:
        await send_error(send, 404, "404 Not Found")
