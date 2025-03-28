from typing import Optional
from pydantic import UUID4, BaseModel, ValidationError
from asyncpg import Record


class AuthUserModel(BaseModel):
    id: UUID4
    username: str
    password: str
    refresh_token: Optional[str]

    @classmethod
    def from_record(cls, data):
        try:
            return cls.model_validate(dict(data))
        except ValidationError:
            return None
