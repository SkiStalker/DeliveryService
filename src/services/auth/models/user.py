from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel


class User(BaseModel):
    id: UUID4
    username: str
    password :str
    first_name: Optional[str]
    second_name: Optional[str]
    patronymic: Optional[str]
    birth: Optional[datetime]
    email: Optional[str]
    phone: Optional[str]
    refresh_token: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]