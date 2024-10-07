FROM python:3.12

RUN pip install "poetry==1.8.3"

WORKDIR /app

COPY pyproject.toml /app/

RUN poetry install

COPY lecture_2 /app/lecture_2

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "lecture_2.hw.shop_api.main:app", "--port", "8000", "--host", "0.0.0.0"]