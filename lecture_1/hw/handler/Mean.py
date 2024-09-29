import re

from lecture_1.hw.handler.base import BaseHandler


class Mean(BaseHandler):
    async def handle(self):
        elements = await self.get_body_as_float_array()
        if elements is not None:
            mean = sum(elements) / len(elements)
            return await self.send_result(mean)

    async def get_body_as_float_array(self):
        body = await self.body()
        body_decoded = body.decode()
        if len(body_decoded) < 2 or body_decoded[0] != '[' or body_decoded[-1] != ']':
            return await self.send_422()
        if body_decoded == '[]':
            return await self.send_400()

        elements = re.split(r',\s*',  body_decoded[1:-1])
        try:
            return [float(i) for i in elements]
        except ValueError:
            return await self.send_422()


