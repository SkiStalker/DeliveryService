from pydantic import BaseModel

from models.decimal_models import Decimal

class PaymentInfoModel(BaseModel):
    delivery_id: str
    currency: str
    cost: Decimal
    company_bank_account_hash: str
    