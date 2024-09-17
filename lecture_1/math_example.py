import math
from http import HTTPStatus
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/factorial")
def get_factorial(n: Annotated[int, Query()]) -> JSONResponse:
    if n < 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid value for n, must be non-negative",
        )

    result = math.factorial(n)

    return JSONResponse({"result": result})


@app.get("/fibonacci/{n}")
def get_fibonacci(n: int) -> JSONResponse:
    if n < 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid value for n, must be non-negative",
        )

    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b

    return JSONResponse({"result": b})


@app.get("/mean")
def get_mean(data: list[float]) -> JSONResponse:
    if len(data) == 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid value for body, must be non-empty array of floats",
        )

    result = sum(data) / len(data)

    return JSONResponse({"result": result})
