import math
import re
from urllib.parse import parse_qs

from lecture_1.hw.errors import send_400, send_422
from lecture_1.hw.util import fibonacci, is_number, read_body, send_response


async def handle_mean(_, receive, send):
    body = await read_body(receive)
    body_decoded = body.decode()
    if len(body_decoded) < 2 or body_decoded[0] != "[" or body_decoded[-1] != "]":
        return await send_422(send)
    if body_decoded == "[]":
        return await send_400(send)

    elements = re.split(r",\s*", body_decoded[1:-1])
    try:
        elements = [float(i) for i in elements]
    except ValueError:
        return await send_422(send)

    mean = sum(elements) / len(elements)
    await send_response(send, 200, f'{{"result": {mean}}}')


async def handle_factorial(scope, _, send):
    qs = scope["query_string"]
    qs = parse_qs(qs)
    if b"n" not in qs or len(qs[b"n"]) > 1 or not is_number(qs[b"n"][0].decode()):
        return await send_422(send)
    n = int(qs[b"n"][0])
    if n < 0:
        return await send_400(send)
    await send_response(send, 200, f'{{"result": {math.factorial(n)}}}')


async def handle_fibonacci(scope, _, send):
    path = scope["path"]
    path_splitted = path.strip("/").split("/")
    if len(path_splitted) != 2 or not is_number(path_splitted[1]):
        return await send_422(send)
    n = int(path_splitted[1])
    if n < 0:
        return await send_400(send)
    await send_response(send, 200, f'{{"result": {fibonacci(n)}}}')
