from datetime import datetime

from pydantic import BaseModel


class ProductHSModel(BaseModel):  # type: ignore
    code_mark_head: str
    code_hs: str
    code_customs: str
    inn_supplier: str
    name: str
    brand: str
    name_supplier: str
    data_in: datetime
