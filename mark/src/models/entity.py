from datetime import date
from enum import IntEnum

from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column

from db.postgres import Base

EMPTY = ""


class StatusEnum(IntEnum):
    """
    Статусы товара ЧЗ:
    0 - Не определено
    1 - На остатках
    2 - Списано
    3 - Есть в ЧЗ нет на остатках
    """

    NOT_DEFINED = 0
    ON_BALANCE = 1
    DEDUCTED = 2
    IN_HS_DEDUCTED = 3

    @property
    def label(self) -> str:
        """Возвращает текстовое описание статуса"""
        return {
            StatusEnum.NOT_DEFINED: "Не определено",
            StatusEnum.ON_BALANCE: "На остатках",
            StatusEnum.DEDUCTED: "Списано",
            StatusEnum.IN_HS_DEDUCTED: "Есть в ЧЗ нет на остатках",
        }[self]


class Product(Base):
    name: Mapped[str]
    code_work: Mapped[int | None]
    code_hs: Mapped[str]
    code_mark_head: Mapped[str] = mapped_column(unique=True)
    code_mark: Mapped[str]
    code_mark_mid: Mapped[str]
    doc_in: Mapped[str]
    data_in: Mapped[date | None]
    doc_out: Mapped[str]
    data_out: Mapped[date | None]
    status: Mapped[int] = mapped_column(
        PgEnum(
            StatusEnum,
            name="product_status_enum",
            create_type=False,
            default=0,
            server_default="NOT_DEFINED",
        )
    )

    def __init__(
        self,
        name: str,
        code_mark_head: str,
        doc_in: str,
        code_mark: str = EMPTY,
        code_mark_mid: str = EMPTY,
        code_work: int | None = None,
        code_hs: str = EMPTY,
        data_in: date | None = None,
        doc_out: str = EMPTY,
        data_out: date | None = None,
        status: int = 0,
    ) -> None:
        self.name = name
        self.code_work = code_work
        self.code_mark_head = code_mark_head
        self.code_mark = code_mark
        self.code_mark_mid = code_mark_mid
        self.doc_in = doc_in
        self.code_hs = code_hs
        self.data_in = data_in
        self.doc_out = doc_out
        self.data_out = data_out
        self.status = status

    def __repr__(self) -> str:
        return str(self.name)


class ProductHS(Base):
    code_mark_head: Mapped[str] = mapped_column(unique=True)
    code_hs: Mapped[str]
    code_customs: Mapped[str]
    inn_supplier: Mapped[str]
    name: Mapped[str]
    brand: Mapped[str]
    name_supplier: Mapped[str]
    data_in: Mapped[date]

    def __init__(
        self,
        code_mark_head: str,
        code_hs: str,
        name: str,
        brand: str,
        data_in: date,
        code_customs: str = EMPTY,
        inn_supplier: str = EMPTY,
        name_supplier: str = EMPTY,
    ) -> None:
        self.code_mark_head = code_mark_head
        self.code_hs = code_hs
        self.name = name
        self.brand = brand
        self.data_in = data_in
        self.code_customs = code_customs
        self.inn_supplier = inn_supplier
        self.name_supplier = name_supplier

    def __repr__(self) -> str:
        return str(self.name)
