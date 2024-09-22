from typing import Dict
from homework_1.math_utils import factorial, fibonacci
from homework_1.utils import send_json_response, receive_body_as_json

async def handle_factorial(send, scope: Dict[str, str]) -> None:
    query_string = scope['query_string'].decode()
    query_params = dict(pair.split('=') for pair in query_string.split('&') if '=' in pair)

    if 'n' not in query_params:
        await send_json_response(send, 422, {"error": "Missing query parameter 'n'"})
        return

    try:
        n = int(query_params['n'])
    except ValueError:
        await send_json_response(send, 422, {"error": "'n' must be an integer"})
        return

    if n < 0:
        await send_json_response(send, 400, {"error": "'n' must be non-negative"})
        return

    result = factorial(n)
    await send_json_response(send, 200, {"result": result})


async def handle_fibonacci(send, path: str) -> None:
    try:
        n = int(path.split('/')[-1])
    except ValueError:
        await send_json_response(send, 422, {"error": "'n' must be an integer"})
        return

    if n < 0:
        await send_json_response(send, 400, {"error": "'n' must be non-negative"})
        return

    result = fibonacci(n)
    await send_json_response(send, 200, {"result": result})


async def handle_mean(receive, send) -> None:
    body = await receive_body_as_json(receive)

    if body is None:
        await send_json_response(send, 422, {"error": "Body is missing or invalid"})
        return

    if not isinstance(body, list) or not all(isinstance(i, (float, int)) for i in body):
        await send_json_response(send, 422, {"error": "Body must be a non-empty array of floats"})
        return

    if len(body) == 0:
        await send_json_response(send, 400, {"error": "Array cannot be empty"})
        return

    result = sum(body) / len(body)
    await send_json_response(send, 200, {"result": result})
