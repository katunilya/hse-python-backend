from typing import Iterable

def _int_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1

_id_generator = _int_id_generator()

def generate_id() -> int:
    return next(_id_generator)