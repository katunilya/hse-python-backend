from typing import Any, Callable, Awaitable

scope_tp = dict[str, Any]
checker_tp = Callable[[scope_tp], bool]
send_tp = Callable[[dict[str, Any]], Awaitable[None]]