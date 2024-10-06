from lecture_1.hw.src.factorial import factorial
from lecture_1.hw.src.fibonacci import fibonacci
from lecture_1.hw.src.mean import mean
from lecture_1.hw.src.utils import send_answer

async def app(scope, receive, send):
    if scope['type'] == 'http' and scope['method'] == 'GET':
        if scope['path'] == '/factorial':
            await factorial(scope, send)
        elif scope['path'].startswith('/fibonacci'):
            await fibonacci(scope, send)
        elif scope['path'] == '/mean':
            await mean(scope, receive, send)
        else:
            await send_answer(send, status_code=404, content_type='text/plain', body=b'404 Not Found')
    else:
        await send_answer(send, status_code=404, content_type='text/plain', body=b'404 Not Found')
