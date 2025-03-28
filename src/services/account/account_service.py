import os
from datetime import datetime, timedelta, timezone
import grpc
from grpc_build.account_service_pb2 import (
    AuthResponse,
    AuthRequest,
    TokenPair,
    RefreshRequest,
    RefreshResponse,
    CheckPermissionsRequest,
    CheckPermissionsResponse,
    LogoutRequest,
    LogoutResponse,
)
from grpc_build.account_service_pb2_grpc import (
    add_AccountServiceServicer_to_server,
    AccountServiceServicer,
)
from grpc import ServicerContext
from jose import JWTError, jwt
from passlib.context import CryptContext
import asyncio
from repositories.user_repository import UserRepository

from clients.redis.tokens_client import TokensClient


SECRET_KEY = os.environ.get(
    "JWT_SECRET_KEY",
    "0797ea423ef4f93f83f556b7414055a58a0ea1e979828c9e7d77dbcb24b50b622b8b33c0735bc939a6cbe87961a7d1a21aae7add625e72e2506f05c18159cbdf029a27a4f9c930ffd773d1f531cdfa331ea7bc89212b17f2202e385527f465f2d636196c5ee386a17399ec17fc36a15675cc4ec2e649a4d72ff3cecb90771af47efb9dc047f00532917ecdd4cba73f6a6173a90516361610e7da11a70e28ef959d4883f8f2c306dca59cecc5d2e19a0112f8513fdb52f62d8ae9245f7ae991e7b7af6a9847d86c2f3624c3d6a3248b460637f32edae8abb6b3019e70e399e9ac64e7d7713876fdf6f282d10ca35079343bd298654d2d661a686c5dfb349d2fe7",
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_token(user_id: str, permissions: set[str], refresh_token: bool = False):
    if refresh_token:
        return create_jwt_token(
            {"sub": user_id, "permissions": [*permissions]},
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
    else:
        return create_jwt_token(
            {"sub": user_id, "permissions": [*permissions]},
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )


class AccountService(AccountServiceServicer):
    def __init__(self, user_rep: UserRepository, tokens_clt: TokensClient):
        super().__init__()
        self._user_rep = user_rep
        self._tokens_clt = tokens_clt

    async def Auth(
        self, request: AuthRequest, context: ServicerContext
    ) -> AuthResponse:
        try:
            user = await self._user_rep.get_user_by_username(request.username)
            if user is not None:
                if pwd_context.verify(request.password, user.password):
                    permissions = await self._user_rep.get_permissions(user.username)

                    access_token = create_token(str(user.id), permissions)
                    refresh_token = create_token(str(user.id), permissions, True)

                    await self._tokens_clt.update_tokens_pair(
                        access_token, refresh_token
                    )

                    await self._user_rep.update_refresh_token(
                        str(user.id), refresh_token
                    )

                    return AuthResponse(
                        code=200,
                        tokens=TokenPair(
                            access_token=access_token, refresh_token=refresh_token
                        ),
                    )
                else:
                    return AuthResponse(code=401, message="Incorrect login or password")
            else:
                return AuthResponse(code=404, message="User with this login not found")
        except Exception as ex:
            return AuthResponse(code=500, message=f"Error : {ex}, args : {ex.args}")

    async def Refresh(
        self, request: RefreshRequest, context: ServicerContext
    ) -> RefreshResponse:
        old_refresh_token = request.refresh_token
        try:
            payload = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

            user_id: str = payload.get("sub")
            permissions: list[str] = payload.get("permissions")

            user = await self._user_rep.get_user_by_id(user_id)

            if (
                user is None
                or user.refresh_token is None
                or user.refresh_token != old_refresh_token
            ):
                return RefreshResponse(code=401, message="Incorrect refresh token")
            else:

                await self._tokens_clt.block_old_tokens_pair(old_refresh_token)

                access_token = create_token(user_id, permissions)
                refresh_token = create_token(user_id, permissions, True)

                await self._tokens_clt.update_tokens_pair(access_token, refresh_token)

                await self._user_rep.update_refresh_token(user_id, refresh_token)

                return AuthResponse(
                    code=200,
                    tokens=TokenPair(
                        access_token=access_token, refresh_token=refresh_token
                    ),
                )
        except jwt.ExpiredSignatureError:
            return RefreshResponse(code=401, message="Refresh token expired")
        except JWTError:
            return RefreshResponse(code=401, message="Invalid refresh token")
        except Exception as ex:
            return RefreshResponse(code=500, message=f"Error : {ex}, args : {ex.args}")

    async def CheckPermissions(
        self, request: CheckPermissionsRequest, context: ServicerContext
    ):
        access_token = request.access_token
        try:
            if await self._tokens_clt.is_access_token_in_black_list(access_token):
                return CheckPermissionsResponse(
                    code=403, message="Access token in blacklist"
                )
            else:
                try:
                    payload = jwt.decode(
                        access_token, SECRET_KEY, algorithms=[ALGORITHM]
                    )
                    
                    permissions: list[str] = payload.get("permissions")
                    user_id = payload.get("sub")
                    
                    if request.permission in permissions:
                        return CheckPermissionsResponse(code=200, user_id=user_id)
                    else:
                        return CheckPermissionsResponse(
                            code=403, message="Access denied"
                        )
                except jwt.ExpiredSignatureError:
                    return RefreshResponse(code=401, message="Access token expired")
                except JWTError:
                    return RefreshResponse(code=401, message="Invalid refresh token")
                except Exception as ex:
                    return RefreshResponse(
                        code=500, message=f"Error : {ex}, args : {ex.args}"
                    )
        except Exception as ex:
            return RefreshResponse(code=500, message=f"Error : {ex}, args : {ex.args}")

    async def Logout(
        self, request: LogoutRequest, context: ServicerContext
    ) -> LogoutResponse:
        access_token = request.access_token
        try:
            payload = jwt.decode(
                access_token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
                options={"verify_exp": False},
            )

            user_id: str = payload.get("sub")

            user = await self._user_rep.get_user_by_id(user_id)
            if not user:
                return LogoutResponse(code=404, message="User not found")

            refresh_token = user.refresh_token

            await self._tokens_clt.block_old_tokens_pair(refresh_token)

            await self._user_rep.remove_user_refresh_token(user_id)

            return LogoutResponse(code=200)
        except JWTError:
            return LogoutResponse(code=401, message="Invalid refresh token")
        except Exception as ex:
            return LogoutResponse(code=500, message=f"Error : {ex}, args : {ex.args}")


async def serve():

    server = grpc.aio.server()

    user_rep = UserRepository()

    tokens_clt = TokensClient()

    await user_rep.connect()
    await tokens_clt.connect()

    add_AccountServiceServicer_to_server(AccountService(user_rep, tokens_clt), server)
    server.add_insecure_port(f"[::]:{os.environ.get("ACCOUNT_SERVICE_PORT", 50051)}")
    print(
        f"Async gRPC Server started at port {os.environ.get("ACCOUNT_SERVICE_PORT", 50051)}"
    )
    await server.start()
    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        pass

    await user_rep.disconnect()
    await tokens_clt.disconnect()


if __name__ == "__main__":
    asyncio.run(serve())
