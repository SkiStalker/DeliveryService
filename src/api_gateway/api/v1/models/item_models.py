from pydantic import BaseModel, ValidationError

from grpc_build.payment_service_pb2 import ItemData
from google.protobuf.json_format import ParseDict


class ItemModel(BaseModel):
    field: str
    value: str

    def to_ItemData(self) -> ItemData:
        return ParseDict(self.model_dump(), ItemData)
