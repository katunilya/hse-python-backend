from fastapi import FastAPI
from api import router

from prometheus_fastapi_instrumentator import Instrumentator
app = FastAPI(title="Shop API")
Instrumentator().instrument(app).expose(app)
app.include_router(router)

# if __name__ == '__main__':
#
#     uvicorn.run(app, port=8001, host='localhost')

