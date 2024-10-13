import json
import math
from http import HTTPStatus

async def app(scope, receive, send):
    if scope["type"] != "http":
        return

    method = scope["method"]
    path = scope["path"]

    if method == "GET" and path == "/factorial":
        await factorial(scope, receive, send)
    elif method == "GET" and path.startswith("/fibonacci/"):
        await fibonacci(scope, receive, send)
    elif method == "GET" and path == "/mean":
        await mean(scope, receive, send)
    else:
        await send_404(send)

async def factorial(scope, receive, send):
    query_string = scope["query_string"].decode("utf-8")
    params = dict(p.split("=") for p in query_string.split("&") if "=" in p)
    
    if "n" not in params:
        await send_422(send, "Query parameter 'n' is required")
        return

    try:
        n = int(params["n"])
    except ValueError:
        await send_422(send, "'n' must be an integer")
        return

    if n < 0:
        await send_400(send, "Invalid value for 'n', must be non-negative")
        return

    result = math.factorial(n)
    await send_json(send, {"result": result})

async def fibonacci(scope, receive, send):
    path_parts = scope["path"].split("/")
    
    try:
        n = int(path_parts[-1])
    except ValueError:
        await send_422(send, "'n' must be an integer")
        return

    if n < 0:
        await send_400(send, "Invalid value for 'n', must be non-negative")
        return

    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b

    await send_json(send, {"result": a})

async def mean(scope, receive, send):
    body = await get_request_body(receive)
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        await send_422(send, "Invalid JSON format")
        return

    if not isinstance(data, list) or not all(isinstance(i, (int, float)) for i in data):
        await send_422(send, "Body must be a non-empty array of floats")
        return

    if len(data) == 0:
        await send_400(send, "Array must not be empty")
        return

    result = sum(data) / len(data)
    await send_json(send, {"result": result})

async def send_404(send):
    await send({
        "type": "http.response.start",
        "status": HTTPStatus.NOT_FOUND,
        "headers": [(b"content-type", b"application/json")],
    })
    await send({
        "type": "http.response.body",
        "body": json.dumps({"error": "Not Found"}).encode("utf-8"),
    })

async def send_400(send, message):
    await send({
        "type": "http.response.start",
        "status": HTTPStatus.BAD_REQUEST,
        "headers": [(b"content-type", b"application/json")],
    })
    await send({
        "type": "http.response.body",
        "body": json.dumps({"error": message}).encode("utf-8"),
    })

async def send_422(send, message):
    await send({
        "type": "http.response.start",
        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
        "headers": [(b"content-type", b"application/json")],
    })
    await send({
        "type": "http.response.body",
        "body": json.dumps({"error": message}).encode("utf-8"),
    })

async def send_json(send, data):
    await send({
        "type": "http.response.start",
        "status": HTTPStatus.OK,
        "headers": [(b"content-type", b"application/json")],
    })
    await send({
        "type": "http.response.body",
        "body": json.dumps(data).encode("utf-8"),
    })

async def get_request_body(receive):
    body = b""
    while True:
        message = await receive()
        if message["type"] == "http.request":
            body += message.get("body", b"")
            if not message.get("more_body"):
                break
    return body