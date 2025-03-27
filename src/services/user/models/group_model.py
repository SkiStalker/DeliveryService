from typing import Optional
from asyncpg import Record
from pydantic import UUID4, BaseModel, ValidationError

from grpc_build.user_service_pb2 import GroupData


class GroupModel(BaseModel):
    id: UUID4
    name: Optional[str] = None

    @classmethod
    def from_grpc_message(cls, grpc_message: GroupData):
        return GroupModel(
            **{desc.name: value for desc, value in grpc_message.ListFields()}
        )

    @classmethod
    def from_record(cls, data: Record):
        try:
            return cls.model_validate(dict(data))
        except ValidationError:
            return None

    def to_GroupData(self) -> GroupData:
        res = self.model_dump(exclude_none=True)
        res["id"] = str(res["id"])
        return GroupData(**res)
