from typing import Optional
from pydantic import UUID4, BaseModel, ValidationError
from grpc_build.user_service_pb2 import UserData


class BriefUserModel(BaseModel):
    id: UUID4
    username: str
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    
    @classmethod
    def from_grpc_message(cls, grpc_message: UserData):
        try:
            return BriefUserModel(**{desc.name : value for desc, value in grpc_message.ListFields()})
        except ValidationError:
            return None