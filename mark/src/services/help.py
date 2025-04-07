import io
import zipfile
from http import HTTPStatus

from fastapi import HTTPException, UploadFile
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


class FileHandler:
    async def validate_zip(self, file_hs: UploadFile) -> None:
        if not file_hs.filename.lower().endswith(".zip"):
            raise HTTPException(HTTPStatus.BAD_REQUEST, "Требуется ZIP-файл")

    async def read_file(self, file_hs: UploadFile) -> bytes:
        try:
            return await file_hs.read()  # type: ignore[no-any-return]
        except Exception as error:
            raise HTTPException(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                f"Ошибка чтения файла: {str(error)}",
            )

    async def extract_csv(self, content_hs: bytes) -> bytes:
        try:
            with zipfile.ZipFile(io.BytesIO(content_hs)) as zf:
                csv_files = [
                    file_csv
                    for file_csv in zf.namelist()
                    if file_csv.lower().endswith(".csv")
                ]
                if not csv_files:
                    raise HTTPException(
                        HTTPStatus.BAD_REQUEST, "В архиве нет CSV файлов"
                    )
                with zf.open(csv_files[0]) as csv_file:
                    return csv_file.read()
        except Exception as error:
            raise HTTPException(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"Ошибка: {str(error)}"
            )
