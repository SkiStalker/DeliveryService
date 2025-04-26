from pydantic import BaseModel, ValidationError

from models.item_models import ItemModel
from grpc_build.payment_service_pb2 import CostRuleData
from google.protobuf.json_format import ParseDict


class CostRuleModel(BaseModel):
    compare_type: str
    data: ItemModel

    def to_CostRuleData(self) -> CostRuleData:
        return ParseDict(self.model_dump(), CostRuleData)
