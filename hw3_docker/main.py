import math
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

# Создаем приложение FastAPI
app = FastAPI()

# Интегрируем Prometheus
Instrumentator().instrument(app).expose(app)

# Пример пути для факториала с параметром в пути
@app.get("/factorial/{n}")
async def get_factorial(n: int):
    if n < 0:
        return {"error": 400}
    return {"result": math.factorial(n)}

# Пример пути для числа Фибоначчи с параметром в пути
@app.get("/fibonacci/{n}")
async def get_fibonacci(n: int):
    if n < 0:
        return {"error": 400}
    return {"result": fibonacci(n)}

# Пример пути для среднего арифметического с параметром в пути
@app.get("/mean/{numbers}")
async def get_mean(numbers: str):
    try:
        num_list = [float(num) for num in numbers.split(',')]
        if not num_list:
            return {"error": 400}
        return {"result": sum(num_list) / len(num_list)}
    except ValueError:
        return {"error": 422}

# Функция для вычисления последовательности Фибоначчи
def fibonacci(n: int):
    sequence = [0, 1]
    for _ in range(2, n):
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]