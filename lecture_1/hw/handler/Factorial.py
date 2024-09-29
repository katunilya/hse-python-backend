import math
from urllib.parse import parse_qs

from lecture_1.hw.handler.base import BaseHandler, is_int


class Factorial(BaseHandler):
    async def handle(self):
        qs = self.scope['query_string']
        qs = parse_qs(qs)
        if b'n' not in qs or len(qs[b'n']) > 1 or not is_int(qs[b'n'][0].decode()):
            return await self.send_422()
        n = int(qs[b'n'][0])
        if n < 0:
            return await self.send_400()
        else:
            return await self.send_result(math.factorial(n))
