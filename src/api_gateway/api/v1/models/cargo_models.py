from typing import Optional
from pydantic import UUID4, BaseModel, ValidationError

from api.v1.models.delivery_models import BriefDeliveryModel

from grpc_build.cargo_service_pb2 import CargoData, CreateCargoData, UpdateCargoData


class CreateCargoModel(BaseModel):
    title: str
    type: str
    description: str
    creator_id: UUID4

    def to_CreateCargoData(self) -> CreateCargoData:
        res = self.model_dump(exclude_none=True)
        res["creator_id"] = str(res["creator_id"])
        return CreateCargoData(**res)


class UpdateCargoModel(BaseModel):
    title: str
    type: str
    description: str
    creator_id: UUID4

    def to_UpdateCargoData(self) -> UpdateCargoData:
        res = self.model_dump(exclude_none=True)
        res["creator_id"] = str(res["creator_id"])
        return UpdateCargoData(**res)
    

class CargoModel(BaseModel):
    id: UUID4
    title: str
    type: str
    description: str
    creator_id: UUID4
    delivery: Optional[BriefDeliveryModel] = None

    @classmethod
    def from_grpc_message(cls, grpc_message: CargoData):
        try:
            cargo_data = {
                desc.name: value for desc, value in grpc_message.ListFields()
            }

            if "delivery_data" in cargo_data:
                cargo_data["delivery_data"] =  BriefDeliveryModel.from_grpc_message(cargo_data["delivery_data"])

            return CargoData(**cargo_data)
        except ValidationError:
            return None