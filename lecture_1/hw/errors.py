from http import HTTPStatus

from lecture_1.hw.util import send_response


async def send_422(send):
    await send_response(
        send, HTTPStatus.UNPROCESSABLE_ENTITY, "422 Unprocessable Entity"
    )


async def send_404(send):
    await send_response(send, HTTPStatus.NOT_FOUND, "404 Not Found")


async def send_400(send):
    await send_response(send, HTTPStatus.BAD_REQUEST, "400 Bad Request")
