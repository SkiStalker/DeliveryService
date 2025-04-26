from pydantic import BaseModel, ValidationError

from grpc_build.payment_service_pb2 import ItemData
from google.protobuf.json_format import MessageToDict

class ItemModel(BaseModel):
    field: str
    value: str

    @classmethod
    def from_grpc_message(cls, grpc_message: ItemData):
        try:
            cost_rule_data = MessageToDict(
                grpc_message,
                preserving_proto_field_name=True,
                use_integers_for_enums=False,
                always_print_fields_with_no_presence=True
            )
            
            return ItemModel(**cost_rule_data)
        except ValidationError:
            return None