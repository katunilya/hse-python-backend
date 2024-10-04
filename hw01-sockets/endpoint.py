import http
from typing import Dict, Callable, Awaitable, Any

SendCallableType = Callable[[http.HTTPStatus, str], Awaitable[Any]]

class Endpoint:
    def __init__(self, path: str, method: http.HTTPMethod):
        self.path = path
        self.method = method

    def match(self, request: Dict[str, str]):
        """
        Проверяет может ли данный Endpoint обработать запрос
        :param request: объект запроса
        """
        pass

    async def handle(self, request: Dict[str, str], send: SendCallableType):
        """
        Обрабатывает запрос и отправляет ответ с помощью функции send.
        :param request: объект запроса
        :param send: функция для отправки ответа
        """
        pass