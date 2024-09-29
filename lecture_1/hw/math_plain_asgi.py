from typing import Any, Awaitable, Callable

import uvicorn

from lecture_1.hw.handler.Factorial import Factorial
from lecture_1.hw.handler.Fibonacci import Fibonacci
from lecture_1.hw.handler.Mean import Mean
from lecture_1.hw.handler.base import Errors


async def app(
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    if scope['type'] == 'lifespan':
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                await send({'type': 'lifespan.shutdown.complete'})
                return
    method = scope['method']
    path = scope['path']
    path_splitted = path.strip('/').split('/')
    if not path_splitted:
        return await Errors.send_404(send)
    match (path_splitted[0], method):
        case ('factorial', 'GET'):
            return await Factorial(scope, receive, send).handle()
        case ('fibonacci', 'GET'):
            return await Fibonacci(scope, receive, send).handle()
        case ('mean', 'GET'):
            return await Mean(scope, receive, send).handle()
        case _:
            return await Errors.send_404(send)


if __name__ == "__main__":
    uvicorn.run("lecture_1.hw.math_plain_asgi:app", port=5000, log_level="info")
