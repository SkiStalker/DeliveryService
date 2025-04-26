from pydantic import BaseModel, ValidationError

from api.v1.models.cost_rule_models import CostRuleModel
from grpc_build.payment_service_pb2 import PaymentInfoData
from models.decimal_models import DecimalModel
from google.protobuf.json_format import MessageToDict


class PaymentInfoModel(BaseModel):
    delivery_id: str
    cost: DecimalModel
    currency: str
    company_bank_account_hash: str
    
    @classmethod
    def from_grpc_message(cls, grpc_message: PaymentInfoData):
        try:
            cost_rule_data = MessageToDict(
                grpc_message,
                preserving_proto_field_name=True,
                use_integers_for_enums=False,
                always_print_fields_with_no_presence=True
            )
            
            return PaymentInfoModel(**cost_rule_data)
        except ValidationError:
            return None

class PaymentRuleModel(BaseModel):
    cost: DecimalModel
    cost_rules: list[CostRuleModel]
    