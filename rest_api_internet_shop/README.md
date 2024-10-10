## Requirements

Python => 3.7 

    pip install -r rest_api_internet_shop/requirements.tx

## Launch

    # Запуск приложения
    uvicorn rest_api_internet_shop.main:app --reload
    #тесты
    poetry run pytest -vv --showlocals --strict tests/test_homework_2.py 

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc
