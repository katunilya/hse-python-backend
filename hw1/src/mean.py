import json
from .utils import send_answer

async def mean(scope, receive, send):
    body = await receive()
    try:
        data = json.loads(body['body'].decode('utf-8'))
    except (ValueError, KeyError):
        await send_answer(send, status_code=422, content_type='text/plain', body=b'422 Unprocessable Entity')
        return

    if not isinstance(data, list) or not all(isinstance(i, (int, float)) for i in data):
        await send_answer(send, status_code=422, content_type='text/plain', body=b'422 Unprocessable Entity')
        return

    if len(data) == 0:
        await send_answer(send, status_code=400, content_type='text/plain', body=b'400 Bad Request')
        return

    result = json.dumps({'result': sum(data) / len(data)}).encode('utf-8')
    await send_answer(send, status_code=200, content_type='application/json', body=result)
