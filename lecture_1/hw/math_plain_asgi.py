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
        # Возвращаем 404 для всех методов, кроме GET
        return await send_response(send, 404, {"error": 404})

    # Обработка запроса на вычисление факториала
    if path == '/factorial':
        query_string = scope['query_string'].decode()
        params = dict(q.split('=') for q in query_string.split('&') if '=' in q)

        # Ошибка 422, если параметр отсутствует или пуст
        if 'n' not in params or not params['n']:
            return await send_response(send, 422, {"error": 422})

        try:
            n = int(params['n'])

            if n < 0:
                # Ошибка 400 для отрицательного числа
                return await send_response(send, 400, {"error": 400})

            result = math.factorial(n)
            return await send_response(send, 200, {'result': result})

        except ValueError:
            # Ошибка 422 для некорректного параметра (например, строка)
            return await send_response(send, 422, {"error": 422})

    # Обработка запроса на вычисление числа Фибоначчи
    elif path == '/fibonacci':
        query_string = scope['query_string'].decode()
        params = dict(q.split('=') for q in query_string.split('&') if '=' in q)

        # Ошибка 422, если параметр отсутствует или пуст
        if 'n' not in params or not params['n']:
            return await send_response(send, 422, {"error": 422})

        try:
            n = int(params['n'])

            if n < 0:
                # Ошибка 400 для отрицательного числа
                return await send_response(send, 400, {"error": 400})

            fib_sequence = fibonacci(n)
            return await send_response(send, 200, {'result': fib_sequence})

        except ValueError:
            # Ошибка 422 для некорректного параметра
            return await send_response(send, 422, {"error": 422})

    # Обработка запроса на вычисление среднего арифметического через строку запроса
    elif path == '/mean':
        query_string = scope['query_string'].decode()
        params = dict(q.split('=') for q in query_string.split('&') if '=' in q)

        # Ошибка 422, если параметр отсутствует или пуст
        if 'numbers' not in params or not params['numbers']:
            return await send_response(send, 422, {"error": 422})

        try:
            # Преобразование строки чисел в список float
            numbers = [float(num) for num in params['numbers'].split(',')]

            if not numbers:
                # Ошибка 400 для пустого списка чисел
                return await send_response(send, 400, {"error": 400})

            result = sum(numbers) / len(numbers)
            return await send_response(send, 200, {'result': result})

        except ValueError:
            # Ошибка 422 для некорректных значений
            return await send_response(send, 422, {"error": 422})

    # Ошибка 404 для неизвестных путей
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
    sequence = [0, 1]
    for _ in range(2, n):
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]