FROM python:3.12

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы для Poetry из корневой директории проекта
COPY pyproject.toml poetry.lock ./

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем зависимости проекта
RUN poetry install --no-root

# Копируем весь код проекта в контейнер
COPY . .

# Открываем порт 8000 для сервиса
EXPOSE 8000

# Запускаем FastAPI сервис через Uvicorn
CMD ["poetry", "run", "uvicorn", "lecture_2.hw.shop_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
