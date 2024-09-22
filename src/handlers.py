# Обработчик для /factorial
import json
import math
from senders import send_400, send_422, send_response


async def handle_factorial(
        scope,
        receive,
        send):

    query_string = scope.get("query_string", b"").decode()
    params = dict(param.split('=')
                  for param in query_string.split('&') if '=' in param)

    if "n" not in params:
        await send_422(send)
        return
    try:
        n = int(params["n"])
        if n < 0:
            await send_400(send, detail="n must be non-negative")
            return
        result = math.factorial(n)
    except ValueError:
        await send_422(send)
        return

    await send_response(send, data={"result": result})


async def handle_fibonacci(scope, receive, send):
    path_parts = scope["path"].split("/")
    if len(path_parts) != 3:
        await send_422(send)
        return

    try:
        n = int(path_parts[2])
        if n < 0:
            await send_400(send, "n must be non-negative")
            return
        result = fibonacci(n)
    except ValueError:
        await send_422(send)
        return

    await send_response(send, {"result": result})


async def handle_mean(scope, receive, send):
    body = await receive()
    try:
        data = json.loads(body.get("body", b"[]"))
        if not isinstance(data, list) or not all(isinstance(x, (int, float)) for x in data):
            await send_422(send)
            return
        if len(data) == 0:
            await send_400(send, "Array must not be empty")
            return
        result = sum(data) / len(data)
    except json.JSONDecodeError:
        await send_422(send)
        return

    await send_response(send, {"result": result})


def fibonacci(n: int) -> int:
    if n == 0:
        return 0
    elif n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
