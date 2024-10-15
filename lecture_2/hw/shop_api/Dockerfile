# Базовый образ на основе Python
FROM python:3.9-slim

# Установка рабочей директории внутри контейнера
WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn prometheus-fastapi-instrumentator

# Копируем весь код приложения в контейнер
COPY . .

# Открываем порт для доступа
EXPOSE 8000

# Команда для запуска приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
