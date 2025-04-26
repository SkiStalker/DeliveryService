from pydantic import BaseModel

from models.decimal_models import DecimalModel


class PaymentInfoModel(BaseModel):
    delivery_id: str
    cost: DecimalModel
    currency: str
    company_bank_account_hash: str