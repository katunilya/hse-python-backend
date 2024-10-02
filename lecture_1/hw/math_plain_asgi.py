import json
from math import factorial
from urllib.parse import parse_qs


async def send_json(send, status: int, content: dict):
    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [
            (b'content-type', b'application/json'),
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': json.dumps(content).encode('utf-8'),
    })


async def receive_request_body(receive):
    body = b""
    more_body = True
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body


def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

async def app(scope, receive, send):
    if scope['type'] != 'http':
        return

    method = scope['method']
    path = scope['path']

    if method == 'GET' and path == '/factorial':
        query_string = scope['query_string'].decode('utf-8')
        query_params = parse_qs(query_string)

        if 'n' not in query_params:
            return await send_json(send, 422, {"error": "Missing 'n' query parameter"})

        try:
            n = int(query_params['n'][0])
        except (ValueError, IndexError):
            return await send_json(send, 422, {"error": "'n' must be an integer"})

        if n < 0:
            return await send_json(send, 400, {"error": "'n' must be non-negative"})

        result = factorial(n)
        return await send_json(send, 200, {"result": result})

    elif method == 'GET' and path.startswith('/fibonacci'):
        try:
            n = int(path.split('/')[-1])
        except ValueError:
            return await send_json(send, 422, {"error": "'n' must be an integer"})

        if n < 0:
            return await send_json(send, 400, {"error": "'n' must be non-negative"})

        result = fibonacci(n)
        return await send_json(send, 200, {"result": result})

    elif method == 'GET' and path == '/mean':
        body = await receive_request_body(receive)

        try:
            data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            return await send_json(send, 422, {"error": "Invalid JSON format"})

        if not isinstance(data, list) or not all(isinstance(i, (int, float)) for i in data):
            return await send_json(send, 422, {"error": "Body must be a list of floats"})

        if len(data) == 0:
            return await send_json(send, 400, {"error": "Array must not be empty"})

        result = sum(data) / len(data)
        return await send_json(send, 200, {"result": result})

    return await send_json(send, 404, {"error": "Not Found"})