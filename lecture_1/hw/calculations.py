import json
from math import factorial
from .utils import *
from .my_types import send_tp
from statistics import mean


async def factorial_asgi(sender: send_tp, *, query=None, received=None, path_params=None) -> None:
    n = query.get('n', '')

    try:
        n = int(n)
        if n < 0:
            await send_content(sender, 400, b'Bad Request')
            return
        await send_content(sender, 200, json.dumps({"result": factorial(n)}).encode("UTF-8"))
    except ValueError:
        await send_content(sender, 422, b'Unprocessable Entity')


async def fibonacci_asgi(sender: send_tp, *, query=None, received=None, path_params=None) -> None:
    n = path_params[0]
    try:
        n = int(n)
        if n < 0:
            await send_content(sender, 400, b'Bad Request')
            return
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        await send_content(sender, 200, json.dumps({"result": a}).encode("UTF-8"))
    except ValueError:
        await send_content(sender, 422, b'Unprocessable Entity')


async def mean_asgi(sender: send_tp, *, query=None, received=None, path_params=None) -> None:
    try:
        mean_list = json.loads(received.get('body', b'').decode('UTF-8'))
    except json.decoder.JSONDecodeError:
        await send_content(sender, 422, b'Unprocessable Entity')
        return
    if mean_list is None:
        await send_content(sender, 422, b'Unprocessable Entity')
        return
    if len(mean_list) == 0:
        await send_content(sender, 400, b'Bad Request')
        return
    try:
        await send_content(sender, 200, json.dumps({"result": mean(mean_list)}).encode("UTF-8"))
    except TypeError:
        await send_content(sender, 422, b'Unprocessable Entity')