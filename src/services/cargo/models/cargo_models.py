from typing import Optional
from pydantic import UUID4, BaseModel, ValidationError

from grpc_build.cargo_service_pb2 import CargoData, CreateCargoData, UpdateCargoData
from grpc_build.cargo_service_pb2 import BriefDeliveryData
from models.delivery_models import BriefDeliveryModel


class CreateCargoModel(BaseModel):
    title: str
    type: str
    description: str
    creator_id: UUID4

    @classmethod
    def from_grpc_message(cls, grpc_message: CreateCargoData):
        try:
            create_cargo_data = {
                desc.name: value for desc, value in grpc_message.ListFields()
            }
            return CreateCargoData(**create_cargo_data)
        except ValidationError:
            return None


class UpdateCargoModel(BaseModel):
    title: str
    type: str
    description: str
    creator_id: UUID4

    @classmethod
    def from_grpc_message(cls, grpc_message: UpdateCargoData):
        try:
            update_user_data = {
                desc.name: value for desc, value in grpc_message.ListFields()
            }
            return UpdateCargoModel(**update_user_data)
        except ValidationError:
            return None
    

class CargoModel(BaseModel):
    id: UUID4
    title: str
    type: str
    description: str
    creator_id: UUID4
    delivery: Optional[BriefDeliveryModel] = None
    
    
    @classmethod
    def from_record(cls, data):
        try:
            return cls.model_validate(dict(data))
        except ValidationError:
            return None

    def to_CargoData(self) -> CargoData:
        res = self.model_dump(exclude_none=True)
        res["id"] = str(res["id"])
        res["creator_id"] = str(res["creator_id"])

        delivery = res.pop("delivery", None)

        if delivery:
            delivery["id"] = str(delivery["id"])
            return CargoData(**res, delivery_data=BriefDeliveryData(**delivery))
        else:
            return CargoData(**res)