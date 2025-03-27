from typing import Optional
from pydantic import UUID4, BaseModel, ValidationError

from grpc_build.user_service_pb2 import GroupData


class GroupModel(BaseModel):
    id: UUID4
    name: Optional[str] = None
    
    @classmethod
    def from_grpc_message(cls, grpc_message: GroupData):
        model_fields = cls.model_fields.keys()
        return GroupModel(**{desc.name : value for desc, value in grpc_message.ListFields() if desc.name in model_fields})

    def to_GroupData(self) -> GroupData:
        res = self.model_dump(exclude_none=True)
        res["id"] = str(res["id"])
        return GroupData(**res)