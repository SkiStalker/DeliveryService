from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import UUID4
from lib.http_tools import make_http_error
from api.v1.routes.account_route import check_permission
from api.v1.models.user_models import BriefUserModel, CreateUserModel, UpdateUserModel, UserModel

from grpc_build.user_service_pb2_grpc import UserServiceStub
from grpc_build.user_service_pb2 import (
    GetUserDataRequest,
    GetUserDataResponse,
    CreateUserRequest,
    CreateUserResponse,
    UpdateUserData,
    UpdateUserDataRequest,
    UpdateUserDataResponse,
    DeactivateUserRequest,
    DeactivateUserResponse,
    ReactivateUserRequest,
    ReactivateUserResponse,
    GetUserDataByUsernameResponse,
    GetUserDataByUsernameRequest,
    SearchUsersRequest,
    SearchUsersResponse,
)

from api.v1.routes.responses.user_responses import (
    get_user_responses,
    get_users_responses,
    update_user_responses,
    delete_user_responses,
    reactivate_user_responses,
    create_user_responses,
    search_users_responses,
    find_user_responses,
)


from context import app


router = APIRouter(prefix="/api/v1/user", tags=["user"])


# GET /users/{user_id} - Получить пользователя по ID (требует аутентификации)
@router.get(
    "/{user_id}",
    response_model=UserModel,
    dependencies=[check_permission("READ_USER")],
    response_model_exclude_unset=True,
    responses=get_user_responses,
)
async def get_user(user_id: UUID4):
    user_stub: UserServiceStub = app.state.user_stub
    resp: GetUserDataResponse = await user_stub.GetUserData(
        GetUserDataRequest(user_id=str(user_id))
    )

    if resp.code == 200:
        return UserModel.from_grpc_message(resp.user_data)
    else:
        make_http_error(resp)


# GET /users/find_user - Получить пользователя по username (требует аутентификации)
@router.get(
    "/find_user",
    response_model=UserModel,
    dependencies=[check_permission("READ_USER")],
    response_model_exclude_unset=True,
    responses=find_user_responses,
)
async def get_user_by_username(username: str = Query(...)):
    user_stub: UserServiceStub = app.state.user_stub
    resp: GetUserDataByUsernameResponse = await user_stub.GetUserDataByUsername(
        GetUserDataByUsernameRequest(username=username)
    )

    if resp.code == 200:
        return UserModel.from_grpc_message(resp.user_data)
    else:
        make_http_error(resp)


# GET /users/search_users Получить пользователей по first_name и second_name (требует аутентификации)
@router.post(
    "/search_users",
    response_model=list[BriefUserModel],
    dependencies=[check_permission("READ_USER")],
    response_model_exclude_unset=True,
    responses=search_users_responses,
)
async def search_users_by_first_name_last_name(
    first_name: str | None = Body(None),
    second_name: str | None = Body(None),
    page: int = Body(...),
):
    user_stub: UserServiceStub = app.state.user_stub
    resp: SearchUsersResponse = await user_stub.SearchUsers(
        SearchUsersRequest(page=page, first_name=first_name, second_name=second_name)
    )

    if resp.code == 200:
        return [BriefUserModel.from_grpc_message(user) for user in resp.users.arr]
    else:
        make_http_error(resp)


# POST /users - Создать нового пользователя (требует аутентификации)
@router.post(
    "/",
    response_model=UserModel,
    dependencies=[check_permission("CREATE_USER")],
    response_model_exclude_unset=True,
    responses=create_user_responses,
)
async def create_user(user: CreateUserModel):
    user_stub: UserServiceStub = app.state.user_stub
    resp: CreateUserResponse = await user_stub.CreateUser(
        CreateUserRequest(creating_user_data=user.to_CreateUserData())
    )

    if resp.code == 201:
        return JSONResponse(
            status_code=201,
            content=UserModel.from_grpc_message(resp.user_data).model_dump(),
        )
    else:
        make_http_error(resp)


@router.put(
    "/{user_id}",
    response_model=UserModel,
    dependencies=[check_permission("UPDATE_USER")],
    response_model_exclude_unset=True,
    responses=update_user_responses,
)
async def update_user(user_id: UUID4, updating_user: UpdateUserModel):
    user_stub: UserServiceStub = app.state.user_stub

    resp: UpdateUserDataResponse = await user_stub.UpdateUserData(
        UpdateUserDataRequest(user_id=str(user_id), updating_user_data=updating_user.to_UpdateUserData())
    )

    if resp.code == 200:
        return UserModel.from_grpc_message(resp.user_data)
    else:
        make_http_error(resp)


# DELETE /users/{user_id} - Удалить пользователя по ID (требует аутентификации)
@router.delete(
    "/{user_id}",
    dependencies=[check_permission("DELETE_USER")],
    response_model_exclude_unset=True,
    responses=delete_user_responses,
)
async def delete_user(user_id: UUID4):
    user_stub: UserServiceStub = app.state.user_stub

    resp: DeactivateUserResponse = await user_stub.DeactivateUser(
        DeactivateUserRequest(user_id=user_id)
    )

    if resp.code == 200:
        return {"detail": "User successfully deactivated"}
    else:
        make_http_error(resp)


@router.post(
    "/reactivate",
    dependencies=[check_permission("REACTIVATE_USER")],
    response_model_exclude_unset=True,
    responses=reactivate_user_responses,
)
async def activate_user(user_id: UUID4):
    user_stub: UserServiceStub = app.state.user_stub

    resp: ReactivateUserRequest = await user_stub.DeactivateUser(
        ReactivateUserResponse(user_id=user_id)
    )

    if resp.code == 200:
        return {"detail": "User successfully reactivated"}
    else:
        make_http_error(resp)
