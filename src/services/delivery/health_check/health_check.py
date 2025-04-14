import os
import grpc


if __name__ == "__main__":
    account_grpc_channel = grpc.aio.insecure_channel(
        f"{os.environ.get("DELIVERY_SERVICE_HOST", "localhost")}:{os.environ.get("DELIVERY_SERVICE_PORT", 50054)}"
    )
    account_grpc_channel.close()
