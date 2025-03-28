import json
from fastapi import APIRouter, Body, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from lib.http_tools import make_http_error
from api.v1.models.token_models import TokenModel
from grpc_build.account_service_pb2 import (
    AuthRequest,
    AuthResponse,
    CheckPermissionsRequest,
    CheckPermissionsResponse,
    LogoutRequest,
    LogoutResponse,
    RefreshRequest,
    RefreshResponse,
)
from grpc_build.account_service_pb2_grpc import AccountServiceStub

from api.v1.routes.responses.account_responses import (
    token_responses,
    refresh_responses,
    logout_responses,
)

from context import app

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/account/token")

router = APIRouter(prefix="/api/v1/account", tags=["account"])


def get_refresh_token(refresh_token: str = Form(...), grant_type: str = Form(...)):

    if grant_type != "refresh_token":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return refresh_token


def check_permission(permission: str):
    async def check_permissions_wrap(access_token=Depends(oauth2_scheme)) -> str:
        account_stub: AccountServiceStub = app.state.account_stub
        resp: CheckPermissionsResponse = await account_stub.CheckPermissions(
            CheckPermissionsRequest(access_token=access_token, permission=permission)
        )
        if resp.code == 200:
            return resp.user_id
        else:
            make_http_error(resp)

    return Depends(check_permissions_wrap)


@router.post("/token", response_model=TokenModel, responses=token_responses)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    account_stub: AccountServiceStub = app.state.account_stub
    resp: AuthResponse = await account_stub.Auth(
        AuthRequest(username=form_data.username, password=form_data.password)
    )

    if resp.code == 200:
        return TokenModel(
            access_token=resp.tokens.access_token,
            refresh_token=resp.tokens.refresh_token,
        )
    else:
        make_http_error(resp)


@router.post("/refresh", response_model=TokenModel, responses=refresh_responses)
async def refresh(refresh_token: str = Depends(get_refresh_token)):
    account_stub: AccountServiceStub = app.state.account_stub
    resp: RefreshResponse = await account_stub.Refresh(
        RefreshRequest(refresh_token=refresh_token)
    )

    if resp.code == 200:
        return TokenModel(
            access_token=resp.tokens.access_token,
            refresh_token=resp.tokens.refresh_token,
        )
    else:
        make_http_error(resp)


@router.post("/logout", responses=logout_responses)
async def logout(token: str = Depends(oauth2_scheme)):
    account_stub: AccountServiceStub = app.state.account_stub
    resp: LogoutResponse = await account_stub.Logout(LogoutRequest(access_token=token))

    if resp.code == 200:
        return {"message": "Success logout"}
    else:
        make_http_error(resp)
