import json
import math
from .utils import send_answer

async def factorial(scope, send):
    query_str = scope['query_string'].decode('utf-8')
    n = query_str.lstrip('n=')

    try:
        n = int(n)
    except ValueError:
        await send_answer(send, status_code=422, content_type='text/plain', body=b'422 Unprocessable Entity')
        return

    if n < 0:
        await send_answer(send, status_code=400, content_type='text/plain', body=b'400 Bad Request')
        return

    result = json.dumps({'result': math.factorial(n)}).encode('utf-8')
    await send_answer(send, status_code=200, content_type='application/json', body=result)
