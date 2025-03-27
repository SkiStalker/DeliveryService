import asyncio
import os
import grpc
from grpc import ServicerContext

from repositories.user_repository import UserRepository

from grpc_build.user_service_pb2_grpc import (
    UserServiceServicer,
    add_UserServiceServicer_to_server,
)

from grpc_build.user_service_pb2 import (
    CreateUserRequest,
    CreateUserResponse,
    GetUserDataRequest,
    GetUserDataResponse,
    UpdateUserDataRequest,
    UpdateUserDataResponse,
    GetAllUsersRequest,
    GetAllUsersResponse,
    ReactivateUserRequest,
    ReactivateUserResponse,
    DeactivateUserRequest,
    DeactivateUserResponse,
    UserData,
)
from models.user_model import UserModel

from passlib.context import CryptContext

from models.group_model import GroupModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(UserServiceServicer):
    def __init__(self, user_rep: UserRepository):
        self._user_rep = user_rep

    async def GetUserData(
        self, request: GetUserDataRequest, context: ServicerContext
    ) -> GetUserDataResponse:
        user_id = request.user_id
        try:
            user = await self._user_rep.get_user_by_id(user_id)

            groups = await self._user_rep.get_user_groups(user_id)

            user.groups = groups

            if user:
                return GetUserDataResponse(code=200, user_data=user.to_UserData())
            else:
                return GetUserDataResponse(
                    code=404, message="User not found or deactivated"
                )
        except Exception as ex:
            return GetUserDataResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )

    async def CreateUser(
        self, request: CreateUserRequest, context
    ) -> CreateUserResponse:
        user_data = request.user_data

        if (
            not user_data.HasField("id")
            or not user_data.HasField("password")
            or not user_data.HasField("groups")
            or len(user_data.groups.arr) == 0
        ):
            return CreateUserResponse(code=400, message="Missing required fields")
        try:
            user = self._user_rep.get_user_by_username(user_data.username)
            if user:
                return CreateUserResponse(
                    code=409, message="User with specified username already exist"
                )
            else:

                create_user_model = UserModel.from_grpc_message(user_data)

                create_user_model.password = pwd_context.hash(
                    create_user_model.password
                )

                created_user = await self._user_rep.create_user(create_user_model)

                if created_user:
                    return CreateUserResponse(
                        code=201, user_data=created_user.to_UserData()
                    )
                else:
                    return CreateUserResponse(code=400, message="Can not create user")
        except Exception as ex:
            return CreateUserResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )

    async def UpdateUserData(
        self, request: UpdateUserDataRequest, context: ServicerContext
    ) -> UpdateUserDataResponse:
        user_data = request.user_data
        try:
            update_user = UserModel.from_grpc_message(user_data)

            if update_user.username is not None:
                check_user = await self._user_rep.get_user_by_username(
                    update_user.username
                )
                if check_user is not None:
                    return UpdateUserDataResponse(
                        code=409, message="User with specified username already exist"
                    )

            if update_user.password is not None:
                update_user.password = pwd_context.hash(update_user.password)

            updated_user_model = await self._user_rep.update_user(update_user)

            if updated_user_model:
                return UpdateUserDataResponse(
                    code=200, user_data=updated_user_model.to_UserData()
                )
            else:
                return UpdateUserDataResponse(
                    code=404, message="User not found or deactivated"
                )
        except Exception as ex:
            return UpdateUserDataResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )

    async def GetAllUsers(
        self, request: GetAllUsersRequest, context: ServicerContext
    ) -> GetAllUsersResponse:
        page = request.page
        try:
            users = await self._user_rep.get_all_users(page)

            return GetAllUsersResponse(users=[user.to_UserData() for user in users])
        except Exception as ex:
            return GetAllUsersResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )

    async def ReactivateUser(
        self, request: ReactivateUserRequest, context: ServicerContext
    ) -> ReactivateUserResponse:
        user_id = request.user_id
        try:
            if await self._user_rep.reactivate_user(user_id):
                return ReactivateUserResponse(code=200)
            else:
                return ReactivateUserResponse(
                    code=404, message="User not found or already activated"
                )
        except Exception as ex:
            return ReactivateUserResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )

    async def DeactivateUser(
        self, request: DeactivateUserRequest, context: ServicerContext
    ) -> DeactivateUserResponse:
        user_id = request.user_id
        try:
            if await self._user_rep.reactivate_user(user_id):
                return DeactivateUserResponse(code=200)
            else:
                return DeactivateUserResponse(
                    code=404, message="User not found or already deactivated"
                )
        except Exception as ex:
            return DeactivateUserResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )


async def serve():

    server = grpc.aio.server()

    user_rep = UserRepository()

    await user_rep.connect()

    add_UserServiceServicer_to_server(UserService(user_rep), server)
    server.add_insecure_port(f"[::]:{os.environ.get("USER_SERVICE_PORT", 50052)}")
    print(
        f"Async gRPC Server started at port {os.environ.get("USER_SERVICE_PORT", 50052)}"
    )
    await server.start()
    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        pass

    await user_rep.disconnect()


if __name__ == "__main__":
    asyncio.run(serve())
