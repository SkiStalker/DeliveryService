from datetime import datetime
from typing import Optional
from asyncpg import Record
from pydantic import UUID4, BaseModel, EmailStr, ValidationError

from models.group_model import GroupModel
from grpc_build.user_service_pb2 import GroupArray, GroupData, UserData


class UserModel(BaseModel):
    id: Optional[UUID4] = None
    username: Optional[str] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    patronymic: Optional[str] = None
    birth: Optional[datetime] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    groups: Optional[list[GroupModel]] = None

    @classmethod
    def from_grpc_message(cls, grpc_message: UserData):
        try:
            user_data = {desc.name: value for desc, value in grpc_message.ListFields()}

            if "groups" in user_data:
                user_data["groups"] = [
                    GroupModel.from_grpc_message(group)
                    for group in user_data["groups"].arr
                ]

            return UserModel(**user_data)
        except ValidationError:
            return None

    @classmethod
    def from_record(cls, data: Record):
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
            return UserData(**res, groups=GroupArray(arr=groups_arr))
        else:
            return UserData(**res)
