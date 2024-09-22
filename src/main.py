from http import HTTPStatus
from typing import Any, Awaitable, Callable

from handlers import handle_factorial, handle_fibonacci, handle_mean


async def app(
        scope: dict[str, Any],
        receive: Callable[[], Awaitable[dict[str, Any]]],
        send: Callable[[dict[str, Any]], Awaitable[None]]):
    """
    !!!
    ASGI-приложение, которое обрабатывает запросы и возвращает ответы.

    :param scope: Словарь, содержащий информацию о запросе. Включает такие ключи, как 'method' (HTTP-метод), 'path' (маршрут запроса), 'headers' (заголовки), и т.д.
    :param receive: Асинхронная функция, которая получает события от клиента (например, данные тела запроса).
    :param send: Асинхронная функция для отправки ответа клиенту. Используется для передачи статуса, заголовков и тела ответа.
    """
    # 1) Проверяем, что запрос поддерживается (только HTTP-протокол)
    if scope["type"] != "http":
        await send({
            "type": "http.response.start",
            "status": HTTPStatus.NOT_FOUND,
            "headers": [[b"content-type", b"application/json"]]
        })
        await send({"type": "http.response.body",
                    "body": b'{"detail": "No support for this protocol."}'})
        return

    #  2) Получаем метод запроса (GET, POST, ETC), путь (/factorial/6)
    method = scope["method"]
    path = scope["path"]

    if method == "GET" and path == "/factorial":
        await handle_factorial(scope, receive, send)
    elif method == "GET" and path.startswith("/fibonacci"):
        await handle_fibonacci(scope, receive, send)
    elif method == "GET" and path == "/mean":
        await handle_mean(scope, receive, send)
    else:
        await send({
            "type": "http.response.start",
            "status": HTTPStatus.NOT_FOUND,
            "headers": [[b"content-type", b"application/json"]]
        })
        await send({"type": "http.response.body", "body": b'{"detail": "This query path not found"}'})
