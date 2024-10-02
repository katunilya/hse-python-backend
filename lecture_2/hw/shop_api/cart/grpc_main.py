from fastapi import HTTPException
import grpc
from . import cart_pb2
from . import cart_pb2_grpc

from ..api.routes import cart_router


# Подключаемся к gRPC серверу
