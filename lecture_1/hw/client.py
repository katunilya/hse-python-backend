import json


async def send_data(send, status, body):
    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [
            [b'content-type', b'text/plain'],
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': json.dumps(body).encode("utf-8"),
    })