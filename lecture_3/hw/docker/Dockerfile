FROM python:3.11 AS base

ARG PYTHONFAULTHANDLER=1
ARG PYTHONHASHSEED=random
ARG PIP_NO_CACHE_DIR=on
ARG PIP_DISABLE_PIP_VERSION_CHECK=on

RUN python -m pip install --upgrade pip
RUN pip install poetry

WORKDIR /app
COPY pyproject.toml poetry.lock /app/
COPY . /app/

RUN poetry install


CMD ["poetry", "run", "uvicorn", "app.myapp:application", "--host", "0.0.0.0", "--port", "8080"]