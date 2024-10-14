# Используем базовый образ Python
FROM python:3.10.6

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости в контейнер
COPY requirements.txt .

COPY test_homework_3.py .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY shop_api/ ./shop_api

# Запуск приложения
CMD ["uvicorn", "shop_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
