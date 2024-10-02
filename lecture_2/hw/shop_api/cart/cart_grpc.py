from concurrent import futures
import grpc
from . import cart_pb2
from . import cart_pb2_grpc

from ..shop.models import Cart

# Хранилище корзин
_carts = dict[int, Cart]()


# gRPC сервис
class CartService(cart_pb2_grpc.CartServiceServicer):
    def CreateCart(self, request, context):
        new_cart_id = len(_carts) + 1
        _carts[new_cart_id] = Cart(id=new_cart_id)
        return cart_pb2.CreateCartResponse(cart_id=new_cart_id)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cart_pb2_grpc.add_CartServiceServicer_to_server(CartService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC server is running on port 50051...")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
