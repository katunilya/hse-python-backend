from typing import Any, Awaitable, Callable


async def application(
    _: dict[str, Any],
    __: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]],
) -> None:
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"text/plain"],
            ],
        }
    )
    await send({"type": "http.response.body", "body": b"Hello, world!"})
