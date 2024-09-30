from typing import Any, Awaitable, Callable

from lecture_1.hw.errors import send_404
from lecture_1.hw.handles import (handle_factorial, handle_fibonacci,
                                  handle_mean)


async def app(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return

    method = scope["method"]
    path = scope["path"]
    path_splitted = path.strip("/").split("/")

    if not path_splitted:
        return await send_404(send)

    match (path_splitted[0], method):
        case ("factorial", "GET"):
            return await handle_factorial(scope, receive, send)
        case ("fibonacci", "GET"):
            return await handle_fibonacci(scope, receive, send)
        case ("mean", "GET"):
            return await handle_mean(scope, receive, send)
        case _:
            return await send_404(send)
