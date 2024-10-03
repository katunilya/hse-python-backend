async def send_answer(send, status_code=404, content_type='text/plain', body=b'404 Not Found', headers=None):
    if headers is None:
        headers = []


    headers.append((b'content-type', content_type.encode('utf-8')))

    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': headers,
    })
    await send({
        'type': 'http.response.body',
        'body': body,
    })
