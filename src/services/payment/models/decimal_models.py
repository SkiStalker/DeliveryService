from pydantic import BaseModel

class Decimal(BaseModel):
    units: int
    nanos: int
    sign: int