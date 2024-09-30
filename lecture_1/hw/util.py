async def send_response(send, status: int, body_str: str):
    body = body_str.encode()
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", b"text/plain"),
            ],
        }
    )

    await send(
        {
            "type": "http.response.body",
            "body": body,
        }
    )


async def read_body(receive):
    res = []
    more_body = True
    while more_body:
        received = await receive()
        res.append(received["body"])
        more_body = received.get("more_body", False)
    return b"".join(res)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def fibonacci(n: int) -> int:
    if n == 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
