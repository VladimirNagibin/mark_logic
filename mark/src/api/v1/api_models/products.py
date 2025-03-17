from datetime import date

from pydantic import BaseModel, ConfigDict

from models.entity import StatusEnum


class Product(BaseModel):  # type: ignore
    name: str
    code_work: int | None
    code_hs: int | None
    code_mark_head: str
    code_mark: str
    doc_in: str
    data_in: date | None
    doc_out: str | None
    data_out: date | None
    status: StatusEnum

    model_config = ConfigDict(from_attributes=True)
