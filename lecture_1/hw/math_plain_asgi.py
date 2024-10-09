import json
import math
from typing import Any, Awaitable, Callable

# Основная ASGI-функция, обрабатывающая запросы
async def app(
    scope: dict[str, Any],
    receive: Callable[[], Awaitable[dict[str, Any]]],
    send: Callable[[dict[str, Any]], Awaitable[None]]
) -> None:

    if scope['type'] != 'http':
        return await send_response(send, 404, {"error": 404})

    method = scope['method']
    path = scope['path']

    if method != 'GET':
        return await send_response(send, 404, {"error": 404})

    # Обработка запроса на вычисление факториала через строку запроса
    if path == '/factorial':
        query_string = scope['query_string'].decode()
        params = dict(q.split('=') for q in query_string.split('&') if '=' in q)

        if 'n' not in params or not params['n']:
            return await send_response(send, 422, {"error": 422})

        try:
            n = int(params['n'])
            if n < 0:
                return await send_response(send, 400, {"error": 400})

            result = math.factorial(n)
            return await send_response(send, 200, {'result': result})

        except ValueError:
            return await send_response(send, 422, {"error": 422})

    # Обработка запроса на вычисление числа Фибоначчи через параметр пути
    elif path.startswith('/fibonacci'):
        try:
            n_str = path.split('/')[2]  # Получаем параметр пути
            n = int(n_str)

            if n < 0:
                return await send_response(send, 400, {"error": 400})

            result = fibonacci(n)
            return await send_response(send, 200, {'result': result})

        except (IndexError, ValueError):
            return await send_response(send, 422, {"error": 422})

    # Обработка запроса на вычисление среднего арифметического через тело запроса (JSON)
    elif path == '/mean':
        body = await receive()
        if 'body' not in body or not body['body']:
            return await send_response(send, 422, {"error": 422})

        try:
            numbers = json.loads(body['body'].decode())
            if not isinstance(numbers, list) or not all(isinstance(num, (int, float)) for num in numbers):
                return await send_response(send, 422, {"error": 422})

            if len(numbers) == 0:
                return await send_response(send, 400, {"error": 400})

            result = sum(numbers) / len(numbers)
            return await send_response(send, 200, {'result': result})

        except json.JSONDecodeError:
            return await send_response(send, 422, {"error": 422})

    return await send_response(send, 404, {"error": 404})

# Функция для отправки HTTP-ответа
async def send_response(
    send: Callable[[dict[str, Any]], Awaitable[None]],
    status: int,
    body: dict
) -> None:
    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [
            (b'content-type', b'application/json')
        ]
    })
    await send({
        'type': 'http.response.body',
        'body': json.dumps(body).encode('utf-8')
    })

# Функция для вычисления последовательности Фибоначчи
def fibonacci(n: int):
    if n == 0:
        return []
    elif n == 1:
        return [0]

    sequence = [0, 1]
    for _ in range(2, n):
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]