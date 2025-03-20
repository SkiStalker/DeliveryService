import json
from fastapi import FastAPI, HTTPException, Depends, status, Request, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import asyncpg

# Секретный ключ для подписи JWT
SECRET_KEY = os.environ.get("API_GATEWAY_SECRET_KEY", 
                            "0797ea423ef4f93f83f556b7414055a58a0ea1e979828c9e7d77dbcb24b50b622b8b33c0735bc939a6cb"
                            "e87961a7d1a21aae7add625e72e2506f05c18159cbdf029a27a4f9c930ffd773d1f531cdfa331ea7bc89"
                            "212b17f2202e385527f465f2d636196c5ee386a17399ec17fc36a15675cc4ec2e649a4d72ff3cecb9077"
                            "1af47efb9dc047f00532917ecdd4cba73f6a6173a90516361610e7da11a70e28ef959d4883f8f2c306dc"
                            "a59cecc5d2e19a0112f8513fdb52f62d8ae9245f7ae991e7b7af6a9847d86c2f3624c3d6a3248b460637"
                            "f32edae8abb6b3019e70e399e9ac64e7d7713876fdf6f282d10ca35079343bd298654d2d661a686c5dfb"
                            "349d2fe7")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

DATABASE_URL = f"postgresql://{os.environ.get("POSTGRES_USER", "postgres")}:{os.environ.get("POSTGRES_PASSWORD", "postgres")}@{os.environ.get("POSTGRES_HOST", "postgres")}:5432/{os.environ.get("POSTGRES_DB", "company")}"
db_pool = None

async def connect_to_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    print("Connected to the database")

async def close_db_connection():
    global db_pool
    await db_pool.close()
    print("Disconnected from the database")


app = FastAPI()

class Refresh:
    refresh_token: str
    grant_type: str
    
    
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Модель данных для пользователя
class User(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str
    age: Optional[int] = None

# Временное хранилище для пользователей
users_db = []

# Псевдо-база данных пользователей
client_db = {
    "admin":  "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # hashed "secret"
}

# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_jwt_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: str):
    return create_jwt_token({"sub": user_id}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(user_id: str):
    return create_jwt_token({"sub": user_id}, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


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

# Зависимости для получения текущего пользователя
def check_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access JWT token have been expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_client(token: str = Depends(oauth2_scheme)):
    return check_token(token)

def refresh_current_client(refresh_body: str =  Body(...)):

    json_refresh_token = parse_refresh_token(refresh_body)
    
    if json_refresh_token:
        refresh_token = json_refresh_token.get("refresh_token", None)
        if refresh_token:
            return check_token(refresh_token)
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

# Маршрут для получения токена
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    password_check = False
    if form_data.username in client_db:
        password = client_db[form_data.username]
        if pwd_context.verify(form_data.password, password):
            password_check = True
            

    if password_check:
        
        access_token = create_access_token(user_id=form_data.username)
        refresh_token = create_refresh_token(user_id=form_data.username)
    
        return Token(access_token=access_token, refresh_token=refresh_token)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/refresh", response_model=Token)
def refresh(current_user: str = Depends(refresh_current_client)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    
    new_access_token = create_access_token(user_id=current_user)
    new_refresh_token = create_refresh_token(user_id=current_user)

    return Token(access_token=new_access_token, refresh_token=new_refresh_token)

# GET /users - Получить всех пользователей (требует аутентификации)
@app.get("/users", response_model=List[User])
def get_users(current_user: str = Depends(get_current_client)):
    return users_db

# GET /users/{user_id} - Получить пользователя по ID (требует аутентификации)
@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, current_user: str = Depends(get_current_client)):
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

# POST /users - Создать нового пользователя (требует аутентификации)
@app.post("/users", response_model=User)
def create_user(user: User, current_user: str = Depends(get_current_client)):
    for u in users_db:
        if u.id == user.id:
            raise HTTPException(status_code=404, detail="User already exist")
    users_db.append(user)
    return user

# PUT /users/{user_id} - Обновить пользователя по ID (требует аутентификации)
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User, current_user: str = Depends(get_current_client)):
    for index, user in enumerate(users_db):
        if user.id == user_id:
            users_db[index] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")

# DELETE /users/{user_id} - Удалить пользователя по ID (требует аутентификации)
@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int, current_user: str = Depends(get_current_client)):
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