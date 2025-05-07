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
    ReactivateUserRequest,
    ReactivateUserResponse,
    DeactivateUserRequest,
    DeactivateUserResponse,
    GetUserDataByUsernameRequest,
    GetUserDataByUsernameResponse,
    SearchUsersRequest,
    SearchUsersResponse,
    BriefUserArray,
)
from models.user_models import UpdateUserModel, UserModel, CreateUserModel

from passlib.context import CryptContext

from models.group_models import GroupModel
from clients.redis.user_cache import UserCache

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

    async def SearchUsers(
        self, request: SearchUsersRequest, context: ServicerContext
    ) -> SearchUsersResponse:
        page = request.page

        first_name = ""
        if request.HasField("first_name"):
            first_name = request.first_name

        second_name = ""
        if request.HasField("second_name"):
            second_name = request.second_name

        try:
            users = await self._user_rep.search_users(page, first_name, second_name)

            return SearchUsersResponse(
                code=200,
                users=BriefUserArray(arr=[user.to_BriefUserData() for user in users]),
            )

        except Exception as ex:
            return SearchUsersResponse(
                code=500, message=f"Error : {ex}, args : {ex.args}"
            )

    async def GetUserDataByUsername(
        self, request: GetUserDataByUsernameRequest, context: ServicerContext
    ) -> GetUserDataByUsernameResponse:
        username = request.username
        try:
            user = await self._user_rep.get_user_by_username(username)

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
        creating_user_data = request.creating_user_data

        if len(creating_user_data.groups.arr) == 0:
            return CreateUserResponse(code=400, message="Missing user group list")
        try:
            exist_user = self._user_rep.get_user_by_username(
                creating_user_data.username
            )
            if exist_user is not None:
                return CreateUserResponse(
                    code=409, message="User with specified username already exist"
                )
            else:

                creating_user_model = CreateUserModel.from_grpc_message(
                    creating_user_data
                )

                creating_user_model.password = pwd_context.hash(
                    creating_user_model.password
                )

                created_user_model = await self._user_rep.create_user(
                    creating_user_model
                )

                if created_user_model is not None:
                    return CreateUserResponse(
                        code=201, user_data=created_user_model.to_UserData()
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
        user_id = request.user_id
        updating_user_data = request.updating_user_data
        try:
            updating_user_model = UpdateUserModel.from_grpc_message(updating_user_data)
            if updating_user_model is not None:
                if updating_user_model.password is not None:
                    updating_user_model.password = pwd_context.hash(
                        updating_user_model.password
                    )

            updated_user_model = await self._user_rep.update_user(
                user_id, updating_user_model
            )

            if updated_user_model is not None:
                return UpdateUserDataResponse(
                    code=200, user_data=updated_user_model.to_UserData()
                )
            else:
                return UpdateUserDataResponse(
                    code=400,
                    message="Failed to update user. Not found user or received data is incorrect.",
                )
        except Exception as ex:
            return UpdateUserDataResponse(
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

    async with UserCache() as user_cache, UserRepository(
        cache_class=user_cache
    ) as user_rep:
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


if __name__ == "__main__":
    asyncio.run(serve())
