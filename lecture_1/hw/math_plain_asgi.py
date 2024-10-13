import math

import json
from urllib.parse import parse_qs


def fib(n):
    arr = [0] * (n + 2)
    arr[0] = 0
    arr[1] = 1
    for i in range(2, n + 1):
        arr[i] = arr[i-1] + arr[i-2]
    return arr[n]


async def send_response(send, status, body, content_type=b'application/json'):
    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [
            [b'content-type', content_type],
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': json.dumps(body).encode('utf-8')
    })


async def get_request_body(receive):
    body = b''
    more_body = True
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)

    return body


async def app(scope, receive, send):
    if scope['method'] != 'GET':
        response_body = 'Not Found'
        await send_response(send, 404, response_body)
        return
        
    path = scope['path'].strip('/').split('/')
    query_string = scope["query_string"].decode('utf-8')
    
    if len(path) == 2 and path[0] == 'fibonacci':
        # будем считать, что последовательность начинается с 0
        if path[1].lstrip('-').isdigit():
            n = int(path[1])
            if n < 0:
                response_body = 'Negative number, only non-negative are supported'
                await send_response(send, 400, response_body)
            else:
                response_body = {'result': fib(n)}
                await send_response(send, 200, response_body)
        else:
            await send_response(send, 422, 'Invalid number format')

    elif path[0] == 'factorial':
        try:
            n = int(parse_qs(query_string).get('n')[0])
            if n < 0:
                response_body = 'Negative number, only non-negative are supported'
                await send_response(send, 400, response_body)
            else:
                response_body = {'result': math.factorial(n)}
                await send_response(send, 200, response_body)
        except:
            response_body = 'Unprocessed entity'
            await send_response(send, 422, response_body)

    elif path[0] == 'mean':
        body = await get_request_body(receive)
        try:
            ns = json.loads(body.decode('utf-8'))
            
            if not ns:
                response_body = 'Bad Request'
                await send_response(send, 400, response_body)
            else:
                response_body = {'result': sum(ns) / len(ns)}
                await send_response(send, 200, response_body)

        except json.JSONDecodeError:
            response_body = 'Unprocessable Entity'
            await send_response(send, 422, response_body)

    else:
        response_body = 'Not Found'
        await send_response(send, 404, response_body)
