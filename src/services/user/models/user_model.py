from datetime import datetime
from typing import Optional
from asyncpg import Record
from pydantic import UUID4, BaseModel, ValidationError

from models.group_model import GroupModel
from grpc_build.user_service_pb2 import UserData


class UserModel(BaseModel):
    id: Optional[UUID4] = None
    username: Optional[str] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    patronymic: Optional[str] = None
    birth: Optional[datetime] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    groups: Optional[list[GroupModel]] = None
    
    @classmethod
    def from_record(cls, data: Record):
        try:
            return cls.model_validate(dict(data))
        except ValidationError:
            return None

    def to_grpc(self):
        res = self.model_dump(exclude_none=True)
        res["id"] = str(res["id"])
        
        if "groups" in res:
            res["groups"] = [GroupModel(**group.to_grpc()) for group in res["groups"]]
            
        return res