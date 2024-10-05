from endpoint import Endpoint
import statistics
import json
import http
import math

from urllib.parse import urlparse, parse_qs


class MeanEndpoint(Endpoint):
    def __init__(self):
        super().__init__(path="/mean", method=http.HTTPMethod.GET)

    def match(self, request) -> bool:
        is_same_method = request.get("method") == self.method.value
        is_same_path = urlparse(request.get('path'))[2] == self.path
        return is_same_method and is_same_path
    
    def _is_array_of_numbers(data):
        if not isinstance(data, list):
            return False
        return all(isinstance(item, (int, float)) for item in data)

    async def handle(self, request, send):
        try:
            data = json.loads(request.get("data"))
            if not data or not MeanEndpoint._is_array_of_numbers(data):
                await send(http.HTTPStatus.BAD_REQUEST, json.dumps({"error" : "Empty or invalid data"}))
            else:
                await send(http.HTTPStatus.OK, json.dumps({"result": (statistics.mean(data))}))
        except ValueError:
                await send(http.HTTPStatus.UNPROCESSABLE_ENTITY, json.dumps({"error" : "Not data"}))

        await send(http.HTTPStatus.OK, "Hello world")


class FactorialEndpoint(Endpoint):
    def __init__(self):
        self.query_param_name = 'n'
        super().__init__(path="/factorial", method=http.HTTPMethod.GET)

    def match(self, request) -> bool:
        path = urlparse(request.get('path'))[2]
        return request.get("method") == self.method.value and path == self.path

    async def handle(self, request, send):
        url_parts = urlparse(request.get('path'))
        params = parse_qs(url_parts[4])
        param = params.get(self.query_param_name, None)
        if not param:
            await send(http.HTTPStatus.UNPROCESSABLE_ENTITY, json.dumps({"error" : "Not a number"}))
        else:
            try:
                param = int(param[0])
                if param < 0:
                    await send(http.HTTPStatus.BAD_REQUEST, json.dumps({"error" : "It's a negative number"}))
                else:
                    await send(http.HTTPStatus.OK, json.dumps({"result": math.factorial(param)}))
            except ValueError:
                await send(http.HTTPStatus.UNPROCESSABLE_ENTITY, json.dumps({"error" : "Not a number"}))


class FibonacciEndpoint(Endpoint):
    def __init__(self):
        super().__init__(path="/fibonacci/", method=http.HTTPMethod.GET)

    def fib(n: int):
        if n == 0:
            return 0
        elif n == 1 or n == 2:
            return 1
        else:
            return FibonacciEndpoint.fib(n-1) + FibonacciEndpoint.fib(n-2)

    def match(self, request) -> bool:
        path = urlparse(request.get('path'))[2]
        return request.get("method") == self.method.value and path.startswith(self.path)

    async def handle(self, request, send):
        url_parts = urlparse(request.get('path'))
        param = url_parts[2].rsplit('/', 1)[-1]

        if not param:
            await send(http.HTTPStatus.UNPROCESSABLE_ENTITY, json.dumps({"error" : "Not a number"}))
        else:
            try:
                if int(param) < 0:
                    await send(http.HTTPStatus.BAD_REQUEST, json.dumps({"error" : "It's a negative number"}))
                else:
                    await send(http.HTTPStatus.OK, json.dumps({"result": FibonacciEndpoint.fib(int(param))}))
            except ValueError:
                await send(http.HTTPStatus.UNPROCESSABLE_ENTITY, json.dumps({"error" : "Not a number"}))