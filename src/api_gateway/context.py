from contextlib import asynccontextmanager
import os
from fastapi import FastAPI
import grpc
from grpc_build.user_service_pb2_grpc import UserServiceStub
from grpc_build.account_service_pb2_grpc import AccountServiceStub

async def connect_to_grpc_account(app: FastAPI):
    app.state.account_grpc_channel = grpc.aio.insecure_channel(f"{os.environ.get("ACCOUNT_SERVICE_HOST", "localhost")}:{os.environ.get("ACOUNT_SERVICE_PORT", 50051)}")
    app.state.account_stub = AccountServiceStub(app.state.account_grpc_channel)
    

async def disconnect_from_grpc_account(app: FastAPI):
    await app.state.account_grpc_channel.close()


async def connect_to_grpc_user(app: FastAPI):
    app.state.user_grpc_channel = grpc.aio.insecure_channel(f"{os.environ.get("USER_SERVICE_HOST", "localhost")}:{os.environ.get("USER_SERVICE_PORT", 50052)}")
    app.state.user_stub = UserServiceStub(app.state.user_grpc_channel)
    
async def disconnect_from_grpc_user(app: FastAPI):
    await app.state.user_grpc_channel.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_grpc_account(app)
    await connect_to_grpc_user(app)
    yield
    await disconnect_from_grpc_user(app)
    await disconnect_from_grpc_account(app)


tags_metadata = [
    {
        "name": "users",
        "description": "Get and update information about all users",
    },
    {
        "name": "account",
        "description": "Login, get tokens and manage self account information",
    },
]

app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata)