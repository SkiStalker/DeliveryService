import os
import grpc


if __name__ == "__main__":
    user_grpc_channel = grpc.aio.insecure_channel(
        f"{os.environ.get("USER_SERVICE_HOST", "localhost")}:{os.environ.get("USER_SERVICE_PORT", 50052)}"
    )
    user_grpc_channel.close()
