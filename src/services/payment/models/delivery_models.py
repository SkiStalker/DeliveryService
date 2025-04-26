from typing import Optional
from pydantic import UUID4, BaseModel, ValidationError


class DeliveryModel(BaseModel):
    id: UUID4
    priority: int
    cargo_type: str
    sender_postal_code: str
    receiver_postal_code: str
    weight: int

    @classmethod
    def from_record(cls, data):
        try:
            return cls.model_validate(dict(data))
        except ValidationError:
            return None
