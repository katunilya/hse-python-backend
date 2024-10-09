from typing import Callable, Dict, Any
from .http_utils import http_error, send_result
import math
import json


async def app(
    scope: Dict[str, Any], receive: Callable[[], Any], send: Callable[[Dict[str, Any]], Any]
) -> None:
    if scope["method"] != "GET":
        await http_error(code=404, message="Not Found", send=send)
        return

    path = scope["path"]

    if path == "/factorial":
        query_string = scope["query_string"].decode("utf-8")
        params = dict(p.split("=") for p in query_string.split("&") if "=" in p)
        if "n" not in params:
            await http_error(code=422, message="Unprocessable Entity", send=send)
            return
        try:
            n = int(params["n"])
        except ValueError:
            await http_error(code=422, message="Unprocessable Entity", send=send)
            return

        if n < 0:
            await http_error(code=400, message="Bad Request", send=send)
            return

        result = math.factorial(n)
        await send_result(result, send)
        return
    if path.startswith("/fibonacci"):
        path_parts = path.split("/")
        try:
            n = int(path_parts[-1])
        except:
            await http_error(code=422, message="Unprocessable Entity", send=send)
            return
        if n < 0:
            await http_error(code=400, message="Bad Request", send=send)
            return

        a, result = 0, 1
        for _ in range(n):
            a, result = result, a + result
        await send_result(result, send)
        return

    if path == "/mean":
        body = await receive()
        try:
            request_body = json.loads(body.get("body", b"").decode())
        except:
            await http_error(code=422, message="Unprocessable Entity", send=send)
            return
        float_list = []
        if not isinstance(request_body, list):
            await http_error(code=422, message="Unprocessable Entity", send=send)
            return

        if len(request_body) == 0:
            await http_error(code=400, message="Bad Request", send=send)
            return

        for item in request_body:
            try:
                float_list.append(float(item))
            except ValueError:
                await http_error(code=422, message="Unprocessable Entity", send=send)
                return
        result = sum(float_list) / len(float_list)
        await send_result(result, send)
        return

    await http_error(code=404, message="Not Found", send=send)
