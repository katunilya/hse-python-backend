from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/mean")
def get_mean(data: list[float]) -> JSONResponse:
    if len(data) == 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid value for body, must be non-empty array of floats",
        )

    result = sum(data) / len(data)

    return JSONResponse({"result": result})
