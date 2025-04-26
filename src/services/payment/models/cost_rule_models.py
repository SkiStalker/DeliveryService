from pydantic import BaseModel, ValidationError

from models.item_models import ItemModel
from grpc_build.payment_service_pb2 import CostRuleData
from google.protobuf.json_format import MessageToDict


class CostRuleModel(BaseModel):
    compare_type: str
    data: ItemModel

    @classmethod
    def from_grpc_message(cls, grpc_message: CostRuleData):
        try:
            cost_rule_data = MessageToDict(
                grpc_message,
                preserving_proto_field_name=True,
                use_integers_for_enums=False,
                always_print_fields_with_no_presence=True
            )
            
            return CostRuleModel(**cost_rule_data)
        except ValidationError:
            return None
