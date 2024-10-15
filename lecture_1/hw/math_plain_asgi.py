from typing import Any, Awaitable, Callable
import json

def factorial(n: int):
    if n == 0:
        return 1
    return n * factorial(n - 1)

def fibonacci(n: int):
    counter = 0
    n1, n2 = 0, 1
    while counter < n:
        nth = n1 + n2
        n1 = n2
        n2 = nth
        counter += 1
    return n2

async def send_content(send: Callable[[dict[str, Any]], Awaitable[None]], 
                       status_code: int, 
                       body: dict[str, Any]):
    await send({
        "type": "http.response.start",
        "status": status_code,
        "headers": [
            [b"content-type", b"application/json"],
        ]
    })
    await send({
        "type": "http.response.body",
        "body": body.encode("utf-8"),
    })

async def app(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return
    if not "path" in scope or not "method" in scope:
        body = {"reason": "Received valid path and method"}
        await send_content(send, 404, json.dumps(body))
        return None
    path = scope["path"]
    method = scope["method"]
    if method != "GET" or not(path.startswith("/factorial") or path.startswith("/fibonacci") or path.startswith("/mean")):
        body = {"reason": f"Received valid path and method {path}, {method}"}
        await send_content(send, 404, json.dumps(body))
        return None
    if path.startswith("/factorial"):
        try:
            n = int(scope["query_string"].decode("ascii").split("=")[-1])
        except ValueError:
            body = {"reason": "Received int type of n"}
            await send_content(send, 422, json.dumps(body))
            return None
        if n < 0:
            body = {"reason": "n should be non-negative number"}
            await send_content(send, 400, json.dumps(body))
            return None
        body = {"result": factorial(n)}
        await send_content(send, 200, json.dumps(body))
    elif path.startswith("/fibonacci"):
        try:
            n = int(path.split("/")[-1])
        except ValueError:
            body = {"reason": "Received n and it should be int"}
            await send_content(send, 422, json.dumps(body))
            return None
        if n < 0:
            body = {"reason": "n should be non-negative number"}
            await send_content(send, 400, json.dumps(body))
            return None
        body = {"result": fibonacci(n)}
        await send_content(send, 200, json.dumps(body))
    elif path.startswith("/mean"):
        body = b""
        more_body = True
        while more_body:
            message = await receive()
            body += message.get("body")
            more_body = message.get("more_body")
        data = json.loads(body.decode("ascii"))
        if not isinstance(data, list) or not all(isinstance(x, (float, int)) for x in data):
            body = {"reason": f"All elements of array should be float {type(data)}"}
            await send_content(send, 422, json.dumps(body))
            return None
        elif not data:
            body = {"reason": "Array is empty"}
            await send_content(send, 400, json.dumps(body))
            return None
        body = {"result": sum(data) / len(data)}
        await send_content(send, 200, json.dumps(body))