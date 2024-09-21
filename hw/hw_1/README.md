# Запуск hw_1

  

1. Скачать код

```bash

git clone  https://github.com/gerfx/aith-python-backend

```

```bash

cd  aith-python-backend

```



3. Создать venv

```bash

python3 -m venv venv

```

4. masOs:

```bash

source  venv/bin/activate

```

windows

```bash

venv\Scripts\activate

```

5. Установка зависимостей

```bash

pip  install  -r requirements.txt

```

6. Заупск сервера

```bash

uvicorn  hw.hw_1.myapp:app  --reload

```

7. Открыть новый терминал в корневой папке проекта

8. Активировать зависимости masOs:

```bash

source  venv/bin/activate

```

windows

```bash

venv\Scripts\activate

```

9. Запустить тесты

```bash

pytest  tests\test_homework_1.py