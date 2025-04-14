from typing import Optional
from pydantic import UUID4, BaseModel, ValidationError

from grpc_build.delivery_service_pb2 import CreateDeliveryData, DeliveryData, SearchDeliveryData, UpdateDeliveryData
from grpc_build.cargo_service_pb2 import BriefDeliveryData


class BriefDeliveryModel(BaseModel):
    id: UUID4
    state: str

    @classmethod
    def from_grpc_message(cls, grpc_message: BriefDeliveryData):
        try:
            delivery_data = {
                desc.name: value for desc, value in grpc_message.ListFields()
            }

            return BriefDeliveryData(**delivery_data)
        except ValidationError:
            return None


class SearchDeliveryModel(BaseModel):
    sender_id: Optional[UUID4]
    receiver_id: Optional[UUID4]

    def to_SearchDeliveryData(self):
        res = self.model_dump(exclude_none=True)
        if "sender_id" in res:
            res["sender_id"] = str(res["sender_id"])
            
        if "receiver_id" in res:
            res["receiver_id"] = str(res["receiver_id"])
        
        return SearchDeliveryData(**res)

class CreateDeliveryModel(BaseModel):
    priority: int
    sender_id: UUID4
    receiver_id: UUID4
    cargo_id: UUID4
    send_address_id: UUID4
    receive_address_id: UUID4

    def to_CreateDeliveryData(self) -> CreateDeliveryData:
        res = self.model_dump(exclude_none=True)
        res["sender_id"] = str(res["sender_id"])
        res["receiver_id"] = str(res["receiver_id"])
        res["cargo_id"] = str(res["cargo_id"])
        res["send_address_id"] = str(res["send_address_id"])
        res["receive_address_id"] = str(res["receive_address_id"])

        return CreateDeliveryData(**res)

class UpdateDeliveryModel(BaseModel):
    state: Optional[str]
    priority: Optional[int]
    receive_address_id: Optional[UUID4]

    def to_UpdateDeliveryData(self) -> UpdateDeliveryData:
        res = self.model_dump(exclude_none=True)
        if "receive_address_id" in res:
            res["receive_address_id"] = str(res["receive_address_id"])

        return UpdateDeliveryData(**res)


class DeliveryModel(BaseModel):
    id: UUID4
    state: str
    priority: int
    sender_id: UUID4
    receiver_id: UUID4
    cargo_id: UUID4
    bill_id: Optional[UUID4]
    send_address_id: UUID4
    receive_address_id: UUID4

    @classmethod
    def from_grpc_message(cls, grpc_message: DeliveryData):
        try:
            delivery_data = {
                desc.name: value for desc, value in grpc_message.ListFields()
            }

            return DeliveryModel(**delivery_data)
        except ValidationError:
            return None

    def to_DeliveryData(self) -> DeliveryData:
        res = self.model_dump(exclude_none=True)
        res["id"] = str(res["id"])
        res["sender_id"] = str(res["sender_id"])
        res["receiver_id"] = str(res["receiver_id"])
        res["cargo_id"] = str(res["cargo_id"])
        res["bill_id"] = str(res["bill_id"])
        res["send_address_id"] = str(res["send_address_id"])
        res["receive_address_id"] = str(res["receive_address_id"])

        return DeliveryData(**res)
