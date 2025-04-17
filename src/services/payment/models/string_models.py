from pydantic import BaseModel

class SearchString(BaseModel):
    field: str
    value: str