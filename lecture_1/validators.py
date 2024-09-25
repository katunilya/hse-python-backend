from typing import Any

def is_number(x: Any) -> bool:
    """This function only checks for real numbers 
    and does not handle complex numbers"""
    return isinstance(x, (int, float))

def str_is_int(x: str) -> bool:
    return x.isdecimal() or x.removeprefix('-').isdecimal()
