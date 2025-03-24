import os
import grpc


if __name__ == "__main__":
    auth_grpc_channel = grpc.aio.insecure_channel(f"{os.environ.get("AUTH_SERVICE_HOST", "localhost")}:{os.environ.get("AUTH_SERVICE_PORT", 50051)}")
    auth_grpc_channel.close()