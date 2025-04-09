from pydantic import UUID4, BaseModel, ValidationError

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