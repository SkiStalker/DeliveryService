from datetime import datetime
from typing import Optional
from asyncpg import Record
from pydantic import UUID4, BaseModel, EmailStr, ValidationError

from api.v1.models.group_models import GroupModel
from grpc_build.user_service_pb2 import (
    GroupArray,
    GroupData,
    UserData,
    CreateUserData,
    UpdateUserData,
    BriefUserData,
)

class BriefUserModel(BaseModel):
    id: UUID4
    username: str
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    
    @classmethod
    def from_grpc_message(cls, grpc_message: BriefUserData):
        try:
            update_user_data = {
                desc.name: value for desc, value in grpc_message.ListFields()
            }
            return BriefUserModel(**update_user_data)
        except ValidationError:
            return None
    
    
class CreateUserModel(BaseModel):
    username: str
    password: str
    first_name: str
    second_name: str
    groups_ids: list[UUID4]
    patronymic: Optional[str] = None
    birth: Optional[datetime] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    
    def to_CreateUserData(self) -> CreateUserData:
        res = self.model_dump(exclude_none=True)
        res["id"] = str(res["id"])
        if "email" in res:
            res["email"] = str(res["email"])
        
        res["groups_ids"] = [str(group_id) for group_id in res["groups_ids"]]
        
        return CreateUserData(**res)

class UpdateUserModel(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    patronymic: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birth: Optional[datetime] = None
    groups: Optional[list[GroupModel]] = None
    
    
    def to_UpdateUserData(self) -> UpdateUserData:
        res = self.model_dump(exclude_none=True)
        if "email" in res:
            res["email"] = str(res["email"])
        
        groups = res.pop("groups", None)
        
        if groups is not None:
            return UpdateUserData(**res, groups=GroupArray(arr=[GroupData(**group) for group in groups]))
        else:
            return UpdateUserData(**res)


class UserModel(BaseModel):
    id: UUID4
    username: str
    first_name: str
    second_name: str
    patronymic: Optional[str] = None
    birth: Optional[datetime] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    groups: list[GroupModel]


    @classmethod
    def from_grpc_message(cls, grpc_message: UpdateUserData):
        try:
            update_user_data = {
                desc.name: value for desc, value in grpc_message.ListFields()
            }

            if "groups" in update_user_data:
                update_user_data["groups"] = [
                    GroupModel.from_grpc_message(group)
                    for group in update_user_data["groups"]
                ]

            return UserModel(**update_user_data)
        except ValidationError:
            return None
