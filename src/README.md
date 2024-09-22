## How to run

1. `poetry install`
2. `poetry shell`
3.  `export PYTHONPATH=$PYTHONPATH:${PWD}/src`
4. `uvicorn src.main:app --reload`



## Info
- <b>scope</b>: Это словарь, описывающий, что было запрошено клиентом – метод запроса, путь, заголовки и т.д. Это аналог мета-информации запроса в FastAPI.
```json

{
    'type': 'http', 
    'http_version': '1.1', 
    'method': 'GET', 
    'path': '/factorial', 
    'query_string': b'n=5',
    'headers': [(b'host', b'localhost')]
}
```

- **receive**: Асинхронная функция, используется для получения событий от клиента. Например, когда клиент отправляет данные в теле запроса, receive позволяет их извлечь.
 
- **send**: Асинхронная функция, используемая для отправки ответа клиенту. С помощью этой функции мы передаем HTTP-заголовки и тело ответа.

