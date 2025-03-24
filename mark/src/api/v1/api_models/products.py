from datetime import date

from pydantic import BaseModel, ConfigDict

from models.entity import StatusEnum


class Product(BaseModel):  # type: ignore
    name: str
    code_work: int | None = None
    code_hs: int | None = None
    code_mark_head: str
    code_mark: str | None = None
    doc_in: str
    data_in: date | None = None
    doc_out: str | None = None
    data_out: date | None = None
    status: StatusEnum

    model_config = ConfigDict(from_attributes=True)


class ProductPutch(BaseModel):  # type: ignore
    name: str | None = None
    code_work: int | None = None
    code_hs: int | None = None
    code_mark: str | None = None
    doc_in: str | None = None
    data_in: date | None = None
    doc_out: str | None = None
    data_out: date | None = None
    status: StatusEnum | None = None

    class Config:
        extra = "forbid"
