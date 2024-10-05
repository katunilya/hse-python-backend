from typing import Callable, Awaitable, List, Any
from .my_types import checker_tp, scope_tp
import re

PATHS_PATTERN = [r'^/factorial$', r'^/fibonacci/.*', '^/mean$']


def is_http(scope: scope_tp) -> bool:
    return scope['type'] == 'http'


def is_get_request(scope: scope_tp) -> bool:
    return scope.get('method', None) == 'GET'


def check_path(scope: scope_tp) -> bool:
    return any(map(lambda x: bool(re.match(x, scope['path'])), PATHS_PATTERN))


def check_request(checkers: List[checker_tp], scope: scope_tp) -> bool:
    return all(map(lambda x: x(scope), checkers))


async def send_content(send: Callable[[dict[str, Any]], Awaitable[None]],
                       response_code: int,
                       body: bin):
    await send({
        'type': 'http.response.start',
        'status': response_code,
        'headers': [
            [b'content-type', b'text/plain'],
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': body,
    })
