FROM python:3.11 AS base

ARG PYTHONFAULTHANDLER=1
ARG PYTHONHASHSEED=random
ARG PIP_NO_CACHE_DIR=on
ARG PIP_DISABLE_PIP_VERSION_CHECK=on

RUN apt-get update && apt-get install -y gcc
RUN python -m pip install --upgrade pip
RUN pip install poetry

WORKDIR $APP_ROOT/src

COPY ./lecture_2 ./poetry.lock ./pyproject.toml ./

#ENV VIRTUAL_ENV=$APP_ROOT/src/.venv \
#    PATH=$APP_ROOT/src/.venv/bin:$PATH

#RUN pip install -r requirements.txt
RUN poetry install

CMD ["poetry", "run", "uvicorn", "hw.shop_api.main:app", "--host", "0.0.0.0", "--port", "8080"]