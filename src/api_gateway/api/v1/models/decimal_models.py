from pydantic import BaseModel, ValidationError

from grpc_build.payment_service_pb2 import DecimalData
from google.protobuf.json_format import MessageToDict, ParseDict


class DecimalModel(BaseModel):
    units: int
    nanos: int
    sign: int

    @classmethod
    def from_grpc_message(cls, grpc_message: DecimalData):
        try:
            cost_rule_data = MessageToDict(
                grpc_message,
                preserving_proto_field_name=True,
                use_integers_for_enums=False,
                always_print_fields_with_no_presence=True,
            )

            return DecimalModel(**cost_rule_data)
        except ValidationError:
            return None

    def to_DecimalData(self) -> DecimalData:
        return ParseDict(self.model_dump(), DecimalData)
