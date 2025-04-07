from datetime import date

from pydantic import BaseModel, ConfigDict

from models.entity import EMPTY, StatusEnum


class Product(BaseModel):  # type: ignore
    name: str
    code_work: int | None = None
    code_hs: str = EMPTY
    code_mark_head: str
    code_mark: str = EMPTY
    code_mark_mid: str = EMPTY
    doc_in: str
    data_in: date | None = None
    doc_out: str = EMPTY
    data_out: date | None = None
    status: StatusEnum = StatusEnum.NOT_DEFINED

    model_config = ConfigDict(from_attributes=True)


class ProductPutch(BaseModel):  # type: ignore
    name: str | None = None
    code_work: int | None = None
    code_hs: str | None = None
    code_mark: str | None = None
    code_mark_mid: str | None = None
    doc_in: str | None = None
    data_in: date | None = None
    doc_out: str | None = None
    data_out: date | None = None
    status: StatusEnum | None = None

    model_config = ConfigDict(extra="forbid")
