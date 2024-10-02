import json
from .utils import send_answer

async def fibonacci(scope, send):
    try:
        n = int(scope['path'].split('/')[-1])
    except ValueError:
        await send_answer(send, status_code=422, content_type='text/plain', body=b'422 Unprocessable Entity')
        return

    if n < 0:
        await send_answer(send, status_code=400, content_type='text/plain', body=b'400 Bad Request')
        return

    def fib(n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    result = json.dumps({'result': fib(n)}).encode('utf-8')
    await send_answer(send, status_code=200, content_type='application/json', body=result)
