
from pydantic import BaseModel


class IDArrayModel(BaseModel):
    ids: list[str]