from datetime import datetime
from typing import Optional
from pydantic import UUID4, BaseModel, ValidationError

from grpc_build.user_service_pb2 import UserData
from models.group_model import GroupModel


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
    def from_grpc_message(cls, grpc_message: UserData):
        try:
            user_data = {desc.name : value for desc, value in grpc_message.ListFields()}
            
            if "groups" in user_data:
                user_data["groups"] = [GroupModel.from_grpc_message(group) for group in user_data["groups"].arr]
            
            return UserModel(**user_data)
        except ValidationError:
            return None
    
    def to_grpc(self):
        res = self.model_dump(exclude_none=True)
        res["id"] = str(res["id"])
        
        if "groups" in res:
            res["groups"] = [GroupModel(**group.to_grpc()) for group in res["groups"]]
            
        return res