from datetime import datetime
from typing import Optional
from asyncpg import Record
from pydantic import UUID4, BaseModel, EmailStr, ValidationError

from models.group_models import GroupModel
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

    def to_BriefUserData(self) -> BriefUserData:
        usr_dmp = self.model_dump(exclude_none=True)
        usr_dmp["id"] = str(usr_dmp["id"])
        
        
        return BriefUserData(**usr_dmp)

    
    @classmethod
    def from_record(cls, data):
        try:
            return cls.model_validate(dict(data))
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

    @classmethod
    def from_grpc_message(cls, grpc_message: CreateUserData):
        try:
            create_user_data = {
                desc.name: value for desc, value in grpc_message.ListFields()
            }
            return UserModel(**create_user_data)
        except ValidationError:
            return None


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

    @classmethod
    def from_grpc_message(cls, grpc_message: UpdateUserData):
        try:
            update_user_data = {
                desc.name: value for desc, value in grpc_message.ListFields()
            }

            if "groups" in update_user_data:
                update_user_data["groups"] = [
                    GroupModel.from_grpc_message(group)
                    for group in update_user_data["groups"].arr
                ]

            return UpdateUserModel(**update_user_data)
        except ValidationError:
            return None


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
    def from_record(cls, data):
        try:
            return cls.model_validate(dict(data))
        except ValidationError:
            return None

    def to_UserData(self) -> UserData:
        res = self.model_dump(exclude_none=True)
        res["id"] = str(res["id"])
        if "email" in res:
            res["email"] = str(res["email"])

        groups = res.pop("groups", None)

        if groups:
            groups_arr = []
            for group in groups:
                group["id"] = str(group["id"])
                groups_arr.append(GroupData(**group))
            return UserData(**res, groups=groups_arr)
        else:
            return UserData(**res)
