async def send_answer(send, status_code=404, content_type='text/plain', body=b'404 Not Found'):
    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': [(b'content-type', content_type)],
    })

    await send({
        'type': 'http.response.body',
        'body': body,
    })
