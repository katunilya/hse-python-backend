import math

def get_factorial(n):
    if n < 0:
        raise ValueError("Invalid value for n, must be non-negative")

    return math.factorial(n)


def get_fibonacci(n: int):
    if n < 0:
        raise ValueError("Invalid value for n, must be non-negative")

    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b

    return b


def get_mean(data: list[float]):
    if len(data) == 0:
        raise ValueError("Invalid value for body, must be non-empty array of floats")

    result = sum(data) / len(data)

    return result
