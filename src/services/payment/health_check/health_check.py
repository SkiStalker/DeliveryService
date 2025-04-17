import os
import grpc


if __name__ == "__main__":
    account_grpc_channel = grpc.aio.insecure_channel(
        f"{os.environ.get("PAYMENT_SERVICE_HOST", "localhost")}:{os.environ.get("PAYMENT_SERVICE_PORT", 50055)}"
    )
    account_grpc_channel.close()
