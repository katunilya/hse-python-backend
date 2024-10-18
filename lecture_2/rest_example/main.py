from fastapi import FastAPI

from lecture_2.rest_example.api import router

app = FastAPI(title="Pokemon REST API Example")

app.include_router(router)
