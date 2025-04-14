import os
import grpc


if __name__ == "__main__":
    cargo_grpc_channel = grpc.aio.insecure_channel(
        f"{os.environ.get("CARGO_SERVICE_HOST", "localhost")}:{os.environ.get("CARGO_SERVICE_PORT", 50053)}"
    )
    cargo_grpc_channel.close()
