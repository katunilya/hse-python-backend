import json
from typing import Dict, List, Optional

async def send_json_response(send, status: int, content: Dict[str, str]) -> None:
    body = json.dumps(content).encode('utf-8')
    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [(b'content-type', b'application/json')],
    })
    await send({
        'type': 'http.response.body',
        'body': body,
    })


async def receive_body_as_json(receive) -> Optional[List[float]]:
    body = b''
    more_body = True
    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)

    if not body:
        return None

    try:
        return json.loads(body.decode('utf-8'))
    except json.JSONDecodeError:
        return None
