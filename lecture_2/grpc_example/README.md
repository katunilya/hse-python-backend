# gRPC Example

```sh
poetry run python -m grpc_tools.protoc \
    --proto_path=./lecture_2/grpc_example/proto/ \
    --python_out=./lecture_2/grpc_example \
    --grpc_python_out=./lecture_2/grpc_example \
    --pyi_out=./lecture_2/grpc_example \
    ping.proto
```

```sh
poetry run python -m lecture_2.grpc_example.example_service
```

```sh
poetry run python -m lecture_2.grpc_example.example_client
```
