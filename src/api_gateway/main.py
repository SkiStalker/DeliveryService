import json
from fastapi import FastAPI, HTTPException, Depends, status, Request, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, UUID4
from typing import List, Literal, Optional
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import os
import asyncpg
from grpc_build.auth_pb2_grpc import AuthServiceStub
from grpc_build.auth_pb2 import AuthRequest, AuthResponse, RefreshResponse, RefreshRequest, LogoutRequest, LogoutResponse, CheckPermissionsRequest, CheckPermissionsResponse

import grpc


auth_grpc_channel: grpc.aio.Channel | None = None
auth_stub: AuthServiceStub | None = None

async def connect_to_grpc_auth():
    global auth_grpc_channel
    global auth_stub
    auth_grpc_channel = grpc.aio.insecure_channel(f"{os.environ.get("AUTH_SERVICE_HOST", "localhost")}:{os.environ.get("AUTH_SERVICE_PORT", 50051)}")
    auth_stub = AuthServiceStub(auth_grpc_channel)
    

async def disconnect_from_grpc_auth():
    global auth_grpc_channel
    await auth_grpc_channel.close()


app = FastAPI(on_startup=[connect_to_grpc_auth], on_shutdown=[disconnect_from_grpc_auth])

class Refresh:
    refresh_token: str
    grant_type: str
    
    
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Модель данных для пользователя
class User(BaseModel):
    id: UUID4
    username: str
    email: str
    hashed_password: str
    age: Optional[int] = None

class Cargo(BaseModel):
    id: UUID4

# Временное хранилище для пользователей
users_db = []


# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def parse_refresh_token(refresh_token_body: str) -> dict | None:
    json_body: dict | None = None
    try:
        json_body = json.loads(refresh_token_body)
    except:
        try:
            json_body = {js_item[0] : js_item[1]  for js_item in [[*item.split("=")] for item in refresh_token_body.split("&")]}
        except:
            pass
    return json_body

def get_refresh_token(refresh_body: str =  Body(...)):

    json_refresh_token = parse_refresh_token(refresh_body)
    
    if json_refresh_token:
        refresh_token = json_refresh_token.get("refresh_token", None)
        if refresh_token:
            return refresh_token
        else:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token was not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token was not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

def check_permissions(token: str = Depends(oauth2_scheme)):
    resp: CheckPermissionsResponse = auth_stub.CheckPermissions(CheckPermissionsRequest(access_token=token))
    if resp.code == 200:
        return
    else:
        raise HTTPException(
            status_code=Literal[resp.code],
            detail=resp.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    

# Маршрут для получения токена
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    
    resp: AuthResponse = await auth_stub.Auth(AuthRequest(username=form_data.username, password=form_data.password))
    
    if resp.code == 200:
        return Token(access_token=resp.tokens.access_token, refresh_token=resp.tokens.refresh_token)
    else:
        raise HTTPException(
            status_code=Literal[resp.code],
            detail=resp.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/refresh", response_model=Token)
async def refresh(refresh_token: str = Depends(get_refresh_token)):
    resp: RefreshResponse = await auth_stub.Refresh(RefreshRequest(refresh_token=refresh_token))
    
    if resp.code == 200:
        return Token(access_token=resp.tokens.access_token, refresh_token=resp.tokens.refresh_token)
    else:
        raise HTTPException(
            status_code=Literal[resp.code],
            detail=resp.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    resp: LogoutResponse = await auth_stub.Logout(LogoutRequest(access_token=token))
    
    if resp.code == 200:
        return {"message": "Success logout"}
    else:
        raise HTTPException(
            status_code=Literal[resp.code],
            detail=resp.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

# GET /users - Получить всех пользователей (требует аутентификации)
@app.get("/users", response_model=List[User])
def get_users(_: str = Depends(check_permissions)):
    return users_db

# GET /users/{user_id} - Получить пользователя по ID (требует аутентификации)
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, _: str = Depends(check_permissions)):
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# POST /users - Создать нового пользователя (требует аутентификации)
@app.post("/users", response_model=User)
def create_user(user: User, _: str = Depends(check_permissions)):
    for u in users_db:
        if u.id == user.id:
            raise HTTPException(status_code=404, detail="User already exist")
    users_db.append(user)
    return user

# PUT /users/{user_id} - Обновить пользователя по ID (требует аутентификации)
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User, _: str = Depends(check_permissions)):
    for index, user in enumerate(users_db):
        if user.id == user_id:
            users_db[index] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")

# DELETE /users/{user_id} - Удалить пользователя по ID (требует аутентификации)
@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int, _: str = Depends(check_permissions)):
    for index, user in enumerate(users_db):
        if user.id == user_id:
            deleted_user = users_db.pop(index)
            return deleted_user
    raise HTTPException(status_code=404, detail="User not found")


# Запуск сервера
# http://localhost:8000/openapi.json swagger
# http://localhost:8000/docs портал документации

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)