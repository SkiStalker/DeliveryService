import asyncio
import os
import grpc
from grpc import ServicerContext

from repositories.user_repository import UserRepository

from grpc_build.user_service_pb2_grpc import UserServiceServicer, add_UserServiceServicer_to_server

from grpc_build.user_service_pb2 import CreateUserRequest, CreateUserResponse, GetUserDataRequest, GetUserDataResponse, UpdateUserDataRequest, UpdateUserDataResponse, GetAllUsersRequest, GetAllUsersResponse, ReactivateUserRequest, ReactivateUserResponse, DeactivateUserRequest, DeactivateUserResponse, UserData
from models.user_model import UserModel

from passlib.context import CryptContext

from models.group_model import GroupModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService(UserServiceServicer):
    def __init__(self, user_rep: UserRepository):
        self._user_rep = user_rep
    
    
    async def GetUserData(self, request: GetUserDataRequest, context: ServicerContext) -> GetUserDataResponse:
        user_id = request.user_id
        
        user = await self._user_rep.get_user_by_id(user_id)
        
        groups = await self._user_rep.get_user_groups(user_id)
        
        user.groups = groups
        
        if user:
            return GetUserDataResponse(code=200, user_data=UserData(
                **user.to_grpc()
            ))
        else:
            return GetUserDataResponse(code=404, message="User not found or deactivated")
    
    async def CreateUser(self, request: CreateUserRequest, context) -> CreateUserResponse:
        user = self._user_rep.get_user_by_username(request.username)
        if user:
            return CreateUserResponse(code=409, message="User with specified username already exist")
        else:
            create_user_data = UserModel(username=request.username)
            
            create_user_data.password = pwd_context.hash(request.password)
            
            if request.HasField("first_name"):
                create_user_data.first_name = request.first_name
            
            if request.HasField("second_name"):
                create_user_data.second_name = request.second_name
                
            if request.HasField("patronymic"):
                create_user_data.patronymic = request.patronymic
            
            if request.HasField("birth"):
                create_user_data.birth = request.birth
            
            if request.HasField("email"):
                create_user_data.email = request.email
            
            if request.HasField("phone"):
                create_user_data.phone = request.phone
            
            
            create_user_data.groups = []
            
            for group_id in request.groups_ids:
                create_user_data.groups.append(GroupModel(group_id))
                
            created_user = await self._user_rep.create_user(create_user_data)
            
            if created_user:
                return CreateUserResponse(code=201, user_data=UserData(**created_user.to_grpc()))
            else:
                return CreateUserResponse(code=400, message="Can not create user")
        
        
    
    async def UpdateUserData(self, request: UpdateUserDataRequest, context: ServicerContext) -> UpdateUserDataResponse:
        user_data = request.user_data
        update_user_data = UserModel(id=user_data.id)
        
        if user_data.HasField("username"):
            update_user_data.username = user_data.username
        
        if user_data.HasField("password"):
            update_user_data.password = pwd_context.hash(user_data.password)
        
        if user_data.HasField("first_name"):
            update_user_data.first_name = user_data.first_name
        
        if user_data.HasField("second_name"):
            update_user_data.second_name = user_data.second_name
            
        if user_data.HasField("patronymic"):
            update_user_data.patronymic = user_data.patronymic
        
        if user_data.HasField("birth"):
            update_user_data.birth = user_data.birth
        
        if user_data.HasField("email"):
            update_user_data.email = user_data.email
        
        if user_data.HasField("phone"):
            update_user_data.phone = user_data.phone
        
        if user_data.HasField("groups"):
            groups = []
            for group in user_data.groups.arr:
                groups.append(GroupModel(id=group.id))
            update_user_data.groups = groups
        
        updated_user = await self._user_rep.update_user(update_user_data)
        
        if updated_user:
            return UpdateUserDataResponse(code=200, user_data=UserData(**updated_user.to_grpc()))
        else:
            return UpdateUserDataResponse(code=404, message="User not found or deactivated")
    
    async def GetAllUsers(self, request: GetAllUsersRequest, context: ServicerContext) -> GetAllUsersResponse:
        page = request.page
        
        users = await self._user_rep.get_all_users(page)
        
        return GetAllUsersResponse(users=[UserData(**user.to_grpc()) for user in users])
    
    async def ReactivateUser(self, request: ReactivateUserRequest, context: ServicerContext) -> ReactivateUserResponse:
        user_id = request.user_id
        
        if await self._user_rep.reactivate_user(user_id):
            return ReactivateUserResponse(code=200)
        else:
            return ReactivateUserResponse(code=404, message="User not found or already activated")
    
    async def DeactivateUser(self, request: DeactivateUserRequest, context: ServicerContext) -> DeactivateUserResponse:
        user_id = request.user_id
        
        if await self._user_rep.reactivate_user(user_id):
            return DeactivateUserResponse(code=200)
        else:
            return DeactivateUserResponse(code=404, message="User not found or already deactivated")
        

async def serve():

    server = grpc.aio.server()
    
    user_rep = UserRepository()
    
    
    await user_rep.connect()
    
    
    add_UserServiceServicer_to_server(UserService(user_rep), server)
    server.add_insecure_port(f"[::]:{os.environ.get("USER_SERVICE_PORT", 50052)}")
    print(f"Async gRPC Server started at port {os.environ.get("USER_SERVICE_PORT", 50052)}")
    await server.start()
    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        pass
    
    await user_rep.disconnect()

if __name__ == '__main__':
    asyncio.run(serve())