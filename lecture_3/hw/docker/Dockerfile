FROM python:3.12

WORKDIR $APP_ROOT/src
COPY ../shop_api ./shop_api
COPY ../requirements.txt ./

RUN pip install -r requirements.txt

CMD ["uvicorn", "shop_api.main:app", "--port", "8080", "--host", "0.0.0.0"]