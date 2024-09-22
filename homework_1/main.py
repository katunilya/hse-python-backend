from typing import Dict
from homework_1.handlers import handle_factorial, handle_fibonacci, handle_mean
from homework_1.utils import send_json_response

async def app(scope: Dict[str, str], receive, send) -> None:
    assert scope['type'] == 'http'

    method = scope['method']
    path = scope['path']

    if method == 'GET' and path == '/factorial':
        await handle_factorial(send, scope)

    elif method == 'GET' and path.startswith('/fibonacci/'):
        await handle_fibonacci(send, path)

    elif method == 'GET' and path == '/mean':
        await handle_mean(receive, send)

    else:
        await send_json_response(send, 404, {"error": "Not Found"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
