from typing import Optional
from asyncpg import Record
from pydantic import UUID4, BaseModel, ValidationError

from grpc_build.user_service_pb2 import GroupData


class GroupModel(BaseModel):
    id: UUID4
    name: Optional[str] = None
    
    @classmethod
    def from_record(cls, data):
        try:
            return cls.model_validate(dict(data))
        except ValidationError:
            return None
