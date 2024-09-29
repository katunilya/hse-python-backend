from lecture_1.hw.handler.base import is_int, BaseHandler


class Fibonacci(BaseHandler):
    async def handle(self):
        path = self.scope['path']
        path_splitted = path.strip('/').split('/')
        if len(path_splitted) != 2 or not is_int(path_splitted[1]):
            return await self.send_422()
        n = int(path_splitted[1])
        if n < 0:
            return await self.send_400()
        res = self.__fibonacci(n)
        return await self.send_result(res)

    @staticmethod
    def __fibonacci(n):
        n0, n1 = 0, 1
        for i in range(n):
            n0, n1 = n1, n0 + n1
        return n1
