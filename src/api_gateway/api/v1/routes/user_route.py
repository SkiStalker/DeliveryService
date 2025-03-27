from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import UUID4

from api.v1.models.brief_user_model import BriefUserModel
from lib.http_tools import make_http_error
from api.v1.routes.account_route import check_permission
from api.v1.models.user_model import UserModel

from grpc_build.user_service_pb2_grpc import UserServiceStub
from grpc_build.user_service_pb2 import GetAllUsersRequest, GetAllUsersResponse, GetUserDataRequest, GetUserDataResponse, CreateUserRequest, CreateUserResponse, UpdateUserDataRequest, UpdateUserDataResponse, DeactivateUserRequest, DeactivateUserResponse, ReactivateUserRequest, ReactivateUserResponse

from grpc_build.user_service_pb2 import GetAllUsersRequest, GetAllUsersResponse, GetUserDataRequest, GetUserDataResponse, CreateUserRequest, CreateUserResponse, UpdateUserDataRequest, UpdateUserDataResponse, DeactivateUserRequest, DeactivateUserResponse, ReactivateUserRequest, ReactivateUserResponse, UserData


from context import app 


router = APIRouter(prefix="/api/v1/users", tags=["users"])

users_db = []

# GET /users - Получить всех пользователей (требует аутентификации)
@router.get("/", response_model=list[BriefUserModel], dependencies=[check_permission("READ_USER")])
async def get_users():
    user_stub: UserServiceStub = app.state.user_stub
    resp: GetAllUsersResponse = await user_stub.GetAllUsers(GetAllUsersRequest())
    
    return [BriefUserModel.from_grpc_message(user) for user in resp.users]

# GET /users/{user_id} - Получить пользователя по ID (требует аутентификации)
@router.get("/{user_id}", response_model=UserModel, dependencies=[check_permission("READ_USER")])
async def get_user(user_id: UUID4):
    user_stub: UserServiceStub = app.state.user_stub
    resp: GetUserDataResponse = await user_stub.GetUserData(GetUserDataRequest(user_id=str(user_id)))
    
    if resp.code == 200:
        return UserModel.from_grpc_message(resp.user_data)
    else:
        make_http_error(resp)
    

# POST /users - Создать нового пользователя (требует аутентификации)
@router.post("/", response_model=UserModel, dependencies=[check_permission("READ_USER")])
async def create_user(user: UserModel):
    user_stub: UserServiceStub = app.state.user_stub
    resp: CreateUserResponse = user_stub.CreateUser(CreateUserRequest(**user.model_dump(exclude_none=True)))
    
    if resp.code == 201:
        return JSONResponse(status_code=201, content=UserModel.from_grpc_message(resp.user_data).model_dump())
    else:
        make_http_error(resp)

@router.put("/{user_id}", response_model=UserModel, dependencies=[check_permission("UPDATE_USER")])
async def update_user(user_id: UUID4, updated_user: UserModel):
    user_stub: UserServiceStub = app.state.user_stub
    
    updated_user.id = user_id
    
    resp: UpdateUserDataResponse = await user_stub.UpdateUserData(UpdateUserDataRequest(user_data=updated_user.to_UserData()))
    
    if resp.code == 200:
        return UserModel.from_grpc_message(resp.user_data)
    else:
        make_http_error(resp)

# DELETE /users/{user_id} - Удалить пользователя по ID (требует аутентификации)
@router.delete("/{user_id}", dependencies=[check_permission("DELETE_USER")])
async def delete_user(user_id: UUID4):
    user_stub: UserServiceStub = app.state.user_stub
    
    resp: DeactivateUserResponse = await user_stub.DeactivateUser(DeactivateUserRequest(user_id=user_id))
    
    if resp.code == 200:
        return {"detail": "User successfully deactivated"}
    else:
        make_http_error(resp)


@router.post("/reactivate", dependencies=[check_permission("REACTIVATE_USER")])
async def activate_user(user_id: UUID4):
    user_stub: UserServiceStub = app.state.user_stub
    
    resp: ReactivateUserRequest = await user_stub.DeactivateUser(ReactivateUserResponse(user_id=user_id))
    
    if resp.code == 200:
        return {"detail": "User successfully reactivated"}
    else:
        make_http_error(resp)