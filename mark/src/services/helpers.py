from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.sql.selectable import Select

from models.entity import Product, ProductHS, StatusEnum


def get_stmt(key: str) -> Select[tuple[Product, ProductHS]]:
    if key == "hs_base":  # Check <is not in the HS> and <is active in the db>.
        return (
            select(Product, ProductHS)
            .select_from(Product)
            .outerjoin(
                ProductHS, Product.code_mark_head == ProductHS.code_mark_head
            )
            .where(
                and_(
                    ProductHS.name.is_(None),
                    Product.status != StatusEnum.DEDUCTED,
                )
            )
        )
    if key == "base_hs":  # Check <is not in db> and <is in HS>.
        return (
            select(Product, ProductHS)
            .select_from(ProductHS)
            .outerjoin(
                Product, Product.code_mark_head == ProductHS.code_mark_head
            )
            .where(Product.name.is_(None))
        )
    if key == "hs_hs":  # Check <is in the HS> and <is not active in the db>.
        return (
            select(Product, ProductHS)
            .join(
                ProductHS, Product.code_mark_head == ProductHS.code_mark_head
            )
            .where(
                Product.status.in_(
                    [StatusEnum.NOT_DEFINED, StatusEnum.DEDUCTED]
                )
            )
        )
    raise HTTPException(
        HTTPStatus.BAD_REQUEST,
        "Not valid key",
    )
