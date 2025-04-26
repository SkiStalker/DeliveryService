from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
import grpc
from grpc_build.payment_service_pb2_grpc import PaymentServiceStub
from grpc_build.delivery_service_pb2_grpc import DeliveryServiceStub
from grpc_build.cargo_service_pb2_grpc import CargoServiceStub
from grpc_build.user_service_pb2_grpc import UserServiceStub
from grpc_build.account_service_pb2_grpc import AccountServiceStub

# TODO Add secure channel
async def get_channel(service_name: str, default_port: int):
    return grpc.aio.insecure_channel(
        f"{os.environ.get(f"{service_name}_SERVICE_HOST", "localhost")}:{os.environ.get(f"{service_name}_SERVICE_PORT", default_port)}"
    )


async def connect_to_grpc_account(app: FastAPI):
    app.state.account_grpc_channel = await get_channel("ACCOUNT", 50051)
    app.state.account_stub = AccountServiceStub(app.state.account_grpc_channel)


async def disconnect_from_grpc_account(app: FastAPI):
    await app.state.account_grpc_channel.close()


async def connect_to_grpc_user(app: FastAPI):
    app.state.user_grpc_channel = await get_channel("USER", 50052)
    app.state.user_stub = UserServiceStub(app.state.user_grpc_channel)


async def disconnect_from_grpc_user(app: FastAPI):
    await app.state.user_grpc_channel.close()


async def connect_to_grpc_cargo(app: FastAPI):
    app.state.cargo_grpc_channel = await get_channel("CARGO", 50053)
    app.state.cargo_stub = CargoServiceStub(app.state.cargo_grpc_channel)


async def disconnect_from_grpc_cargo(app: FastAPI):
    await app.state.cargo_grpc_channel.close()


async def connect_to_grpc_delivery(app: FastAPI):
    app.state.delivery_grpc_channel = await get_channel("DELIVERY", 50054)
    app.state.delivery_stub = DeliveryServiceStub(app.state.delivery_grpc_channel)


async def disconnect_from_grpc_delivery(app: FastAPI):
    await app.state.delivery_grpc_channel.close()


async def connect_to_grpc_payment(app: FastAPI):
    app.state.payment_grpc_channel = await get_channel("PAYMENT", 50055)
    app.state.payment_stub = PaymentServiceStub(app.state.payment_grpc_channel)

async def disconnect_from_grpc_payment(app: FastAPI):
    await app.state.payment_grpc_channel.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_grpc_account(app)
    await connect_to_grpc_user(app)
    await connect_to_grpc_cargo(app)
    await connect_to_grpc_delivery(app)
    await connect_to_grpc_payment(app)
    yield
    await disconnect_from_grpc_payment(app)
    await disconnect_from_grpc_delivery(app)
    await disconnect_from_grpc_cargo(app)
    await disconnect_from_grpc_user(app)
    await disconnect_from_grpc_account(app)


tags_metadata = [
    {
        "name": "user",
        "description": "Get and update information about all users",
    },
    {
        "name": "account",
        "description": "Login, get tokens and manage self account information",
    },
    {
        "name": "cargo",
        "description": "Create, get and update cargo information",
    },
    {
        "name": "delivery",
        "description": "Create, get and update delivery information",
    },
    {
        "name": "payment",
        "description": "Get payment info, confirm payment"
    }
]

app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata)
