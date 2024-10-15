# Устанавливаем Python
FROM python:3.12-slim

# Устанавливаем переменные окружения
ENV POETRY_VERSION=1.8.3
ENV POETRY_VIRTUALENVS_CREATE=false

# Устанавливаем Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем pyproject.toml и poetry.lock из корня проекта в контейнер
COPY ./pyproject.toml ./poetry.lock /app/

# Устанавливаем зависимости через Poetry
RUN poetry install --no-root --no-dev

# Копируем весь проект в контейнер
COPY ./ /app/

# Открываем порт для приложения
EXPOSE 8000

# Запускаем приложение с указанием PYTHONPATH
CMD ["sh", "-c", "PYTHONPATH=/app uvicorn lecture_2.hw.shop_api.main:app --host 0.0.0.0 --port 8000"]
