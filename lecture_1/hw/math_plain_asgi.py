import json
import math
from urllib.parse import parse_qs


async def app(scope, receive, send):
    if scope['type'] == 'http':
        if scope['path'] == '/factorial' and scope['method'] == 'GET':
            await factorial(scope, send)
        elif scope['path'].startswith('/fibonacci') and scope['method'] == 'GET':
            await fibonacci(scope, send)
        elif scope['path'].startswith('/mean') and scope['method'] == 'GET':
            await mean(scope, receive, send)
        else:
            await send_answer(send, status_code=404, content_type='text/plain', body=b'404 Not Found')
    else:
        await send_answer(send, status_code=404, content_type='text/plain', body=b'404 Not Found')


async def send_answer(send,
                      status_code: int = 404,
                      content_type: str = 'text/plain',
                      body: bytes = b'404 Not Found',
                      ) -> None:
    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': [(b'content-type', content_type.encode('utf-8'))],
    })

    await send({
        'type': 'http.response.body',
        'body': body,
    })


async def factorial(scope, send):
    query_str = scope['query_string'].decode('utf-8')
    params = parse_qs(query_str)
    n = params.get('n', [None])[0]

    try:
        n = int(n)
    except (ValueError, TypeError):
        await send_answer(send, status_code=422, content_type='text/plain', body=b'422 Unprocessable Entity')
        return

    if n < 0:
        await send_answer(send, status_code=400, content_type='text/plain', body=b'400 Bad Request')
        return

    result = json.dumps({'result': math.factorial(n)}).encode('utf-8')
    await send_answer(send, status_code=200, content_type='application/json', body=result)


async def fibonacci(scope, send):
    path = scope['path'].rstrip('/').split('/')
    try:
        n = int(path[-1])
    except ValueError:
        await send_answer(send, status_code=422, content_type='text/plain', body=b'422 Unprocessable Entity')
        return

    if n < 0:
        await send_answer(send, status_code=400, content_type='text/plain', body=b'400 Bad Request')
        return
    
    a, b = 0, 1

    for _ in range(n - 2):
        a, b = b, a + b 
    result = b if n > 1 else a

    result_json = json.dumps({'result': result}).encode('utf-8')
    await send_answer(send, status_code=200, content_type='application/json', body=result_json)


async def mean(scope, receive, send):
    if scope["method"] != "GET":
        await send_answer(send, 404, content_type="text/plain", body=b"404 Not Found")
        return

    request = await receive()
    body = request.get("body", b"")

    if not body:
        await send_answer(send, 422, content_type="text/plain", body=b"422 Unprocessable Entity")
        return

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        await send_answer(send, 400, content_type="text/plain", body=b"400 Bad Request")
        return
    if isinstance(data, list) and not len(data):
        await send_answer(send, 400, content_type="text/plain", body=b"400 Bad Request")
        return
    if not data:
        await send_answer(send, 422, content_type="text/plain", body=b"422 Unprocessable Entity")
        return

    try:
        float_sum = sum(el for el in data if isinstance(el, (int, float)))
        mean_value = float_sum / len(data)
    except TypeError:
        await send_answer(send, 422, content_type="text/plain", body=b"422 Unprocessable Entity")
        return

    result = json.dumps({"result": mean_value}).encode('utf-8')
    await send_answer(send, status_code=200, content_type="application/json", body=result)