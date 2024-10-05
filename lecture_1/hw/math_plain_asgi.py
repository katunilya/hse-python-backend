from typing import Callable, Awaitable, List
from .calculations import *
from .my_types import checker_tp, send_tp
from urllib.parse import parse_qs
from .utils import *

CHECK_FUNCTIONS: List[checker_tp] = [is_http, is_get_request, check_path]

CALCULATIONS: dict[str, Callable] = {
    'factorial': factorial_asgi,
    'fibonacci': fibonacci_asgi,
    'mean': mean_asgi
}


async def app(scope: dict[str, Any],
              receive: Callable[[], Awaitable[dict[str, Any]]],
              send: send_tp) -> None:
    if not check_request(CHECK_FUNCTIONS, scope):
        await send_content(send, 404, b'Not found')
        return
    _, func, *path_par = scope['path'].split('/')
    query_params = {k: v[0] for (k, v) in parse_qs(scope['query_string'].decode("UTF-8")).items()}
    received = await receive()
    await CALCULATIONS[func](send, received=received, path_params=path_par, query=query_params)
