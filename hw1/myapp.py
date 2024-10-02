from hw1.src.factorial import factorial
from hw1.src.fibonacci import fibonacci
from hw1.src.mean import mean
from hw1.src.utils import send_answer

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
