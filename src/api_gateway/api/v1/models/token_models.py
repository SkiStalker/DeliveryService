from pydantic import BaseModel, ValidationError


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
