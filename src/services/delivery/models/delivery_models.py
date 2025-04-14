from typing import Optional
from pydantic import UUID4, BaseModel, ValidationError

from grpc_build.delivery_service_pb2 import (
    CreateDeliveryData,
    DeliveryData,
    SearchDeliveryData,
    UpdateDeliveryData,
)


class SearchDeliveryModel(BaseModel):
    sender_id: Optional[UUID4]
    receiver_id: Optional[UUID4]

    @classmethod
    def from_grpc_message(cls, grpc_message: SearchDeliveryData):
        try:
            create_delivery_data = {
                desc.name: value for desc, value in grpc_message.ListFields()
            }
            return SearchDeliveryModel(**create_delivery_data)
        except ValidationError:
            return None


class CreateDeliveryModel(BaseModel):
    priority: int
    sender_id: UUID4
    receiver_id: UUID4
    cargo_id: UUID4
    send_address_id: UUID4
    receive_address_id: UUID4

    @classmethod
    def from_grpc_message(cls, grpc_message: CreateDeliveryData):
        try:
            create_delivery_data = {
                desc.name: value for desc, value in grpc_message.ListFields()
            }
            return CreateDeliveryModel(**create_delivery_data)
        except ValidationError:
            return None


class UpdateDeliveryModel(BaseModel):
    state: Optional[str]
    priority: Optional[int]
    receive_address_id: Optional[UUID4]

    @classmethod
    def from_grpc_message(cls, grpc_message: UpdateDeliveryData):
        try:
            update_delivery_data = {
                desc.name: value for desc, value in grpc_message.ListFields()
            }
            return UpdateDeliveryModel(**update_delivery_data)
        except ValidationError:
            return None


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
    def from_record(cls, data):
        try:
            return cls.model_validate(dict(data))
        except ValidationError:
            return None

    def to_DeliveryData(self) -> DeliveryData:
        res = self.model_dump(exclude_none=True)
        res["id"] = str(res["id"])
        res["sender_id"] = str(res["sender_id"])
        res["receiver_id"] = str(res["receiver_id"])
        res["cargo_id"] = str(res["cargo_id"])

        if "bill_id" in res:
            res["bill_id"] = str(res["bill_id"])

        res["send_address_id"] = str(res["send_address_id"])
        res["receive_address_id"] = str(res["receive_address_id"])

        return DeliveryData(**res)
