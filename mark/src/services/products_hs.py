import asyncio
import io
import zipfile
from abc import ABC, abstractmethod
from functools import lru_cache
from http import HTTPStatus
from typing import Any

import pandas as pd
from fastapi import Depends, HTTPException, UploadFile
from pandas import DataFrame
from pydantic import ValidationError
from sqlalchemy import Row, Sequence, delete, insert
from sqlalchemy.exc import (
    DataError,
    IntegrityError,
    InternalError,
    OperationalError,
    ProgrammingError,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.api_models.products_hs import ProductHSModel
from core.logger import logger
from db.postgres import get_session
from models.entity import Product, ProductHS
from services.helpers import get_stmt


class AbstractProductHSRepository(ABC):

    @abstractmethod
    async def load_data(self, df: DataFrame) -> None:
        """
        Method for load data from DataFrame.
        """
        ...

    @abstractmethod
    async def clear(self) -> None:
        """
        Method for clear table.
        """
        ...

    @abstractmethod
    async def get_incorrect(
        self, key: str
    ) -> Sequence[Row[tuple[Product, ProductHS]]]:
        """
        Method for check table.
        """
        ...


class ProductHSRepository(AbstractProductHSRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def load_data(self, df: DataFrame) -> None:

        data: list[dict[str, Any]] = df.to_dict(orient="records")
        try:
            validated_data = [
                ProductHSModel(**item).model_dump() for item in data
            ]
        except ValidationError as e:
            logger.error(f"Validation failed: {e.json()}")
            raise HTTPException(
                HTTPStatus.UNPROCESSABLE_ENTITY, "Некорректные данные"
            ) from e
        stmt = insert(ProductHS).values(validated_data)
        try:
            await self.session.execute(stmt)
            await self.session.commit()
        except IntegrityError as e:
            # Нарушение целостности данных
            await self.session.rollback()
            logger.error(f"Integrity Error: {str(e)}")
            raise HTTPException(
                HTTPStatus.CONFLICT,
                "Конфликт данных (дубликаты, внешние ключи)",
            )

        except DataError as e:
            # Некорректные типы данных
            await self.session.rollback()
            logger.error(f"Data Error: {str(e)}")
            raise HTTPException(
                HTTPStatus.BAD_REQUEST, "Некорректный формат данных"
            )

        except OperationalError as e:
            # Проблемы подключения к БД
            await self.session.rollback()
            logger.critical(f"Operational Error: {str(e)}")
            raise HTTPException(
                HTTPStatus.SERVICE_UNAVAILABLE,
                "Ошибка подключения к базе данных",
            )

        except ProgrammingError as e:
            # Ошибки в SQL-запросе
            await self.session.rollback()
            logger.error(f"Programming Error: {str(e)}")
            raise HTTPException(
                HTTPStatus.BAD_REQUEST, "Ошибка в запросе к базе данных"
            )

        except InternalError as e:
            # Внутренние ошибки PostgreSQL
            await self.session.rollback()
            logger.critical(f"Internal DB Error: {str(e)}")
            raise HTTPException(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Внутренняя ошибка базы данных",
            )

        except SQLAlchemyError as e:
            # Все остальные ошибки SQLAlchemy
            await self.session.rollback()
            logger.error(f"SQLAlchemy Error: {str(e)}")
            raise HTTPException(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Неизвестная ошибка базы данных",
            )

        except Exception as e:
            # Непредвиденные ошибки
            await self.session.rollback()
            logger.critical(f"Unexpected Error: {str(e)}")
            raise HTTPException(
                HTTPStatus.INTERNAL_SERVER_ERROR, "Критическая ошибка сервера"
            )

    async def clear(self) -> None:
        try:
            stmt = delete(ProductHS)
            await self.session.execute(stmt)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                f"Ошибка базы данных: {str(e)}",
            )

    async def get_incorrect(
        self, key: str
    ) -> Sequence[Row[tuple[Product, ProductHS]]]:
        stmt = get_stmt(key)
        try:
            results = await self.session.execute(stmt)
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                f"Ошибка базы данных: {str(e)}",
            )
        return results.all()


class ProductHSService:

    COLUMN_MAPPING: dict[str, str] = {
        "Код": "code_mark_head",  # Пример: колонка в CSV → колонка в БД
        "GTIN": "code_hs",
        "Код ТН ВЭД": "code_customs",
        "Производитель / Импортер": "inn_supplier",
        "Наименование товара": "name",
        "Бренд": "brand",
        "Наименование производителя": "name_supplier",
        "Дата ввода в оборот": "data_in",
    }

    def __init__(self, repository: AbstractProductHSRepository):
        self.repository = repository

    async def load_data(self, df: DataFrame) -> None:
        await self.repository.load_data(df)

    async def clear(self) -> None:
        await self.repository.clear()

    async def check(
        self, key: str
    ) -> Sequence[Row[tuple[Product, ProductHS]]]:
        res = await self.repository.get_incorrect(key)
        return res

    @staticmethod
    async def get_csv_from_zip(file: UploadFile) -> bytes:
        if not file.filename.lower().endswith(".zip"):
            raise HTTPException(HTTPStatus.BAD_REQUEST, "Требуется ZIP-файл")

        try:
            # Чтение ZIP
            content = await file.read()

            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                # Поиск первого CSV
                csv_files = [
                    f for f in zf.namelist() if f.lower().endswith(".csv")
                ]
                if not csv_files:
                    raise HTTPException(
                        HTTPStatus.BAD_REQUEST, "В архиве нет CSV файлов"
                    )

                # Обработка первого CSV
                with zf.open(csv_files[0]) as csv_file:
                    csv_content = csv_file.read()
                    return csv_content
        except Exception as e:
            raise HTTPException(
                HTTPStatus.INTERNAL_SERVER_ERROR, f"Ошибка: {str(e)}"
            )

    async def process_csv(self, content: bytes) -> pd.DataFrame:
        """Обработка CSV с переименованием колонок"""
        # Чтение CSV через отдельный поток (pandas блокирующий)
        csv_params: dict[str, Any] = {
            "index_col": False,  # Явно отключаем индекс
            "skiprows": 1,  # Пропускаем строку фильтра и заголовок
            "header": 0,  # Используем следующую строку как заголовок
            "usecols": list(self.COLUMN_MAPPING.keys()),
            "on_bad_lines": "skip",  # Пропускаем битые строки
            "dtype": {
                "GTIN": str,  # Явно указываем тип как строка
                "Код ТН ВЭД": str,
                "Производитель / Импортер": str,
            },
            #  "parse_dates": ["Дата ввода в оборот"], # Автоматический парсинг
            #  "date_parser": lambda x: datetime.strptime(
            #    x, "%Y-%m-%dT%H:%M:%S.%fZ"
            #  ),
            "keep_default_na": False,  # Отключить автомат преобразование в NaN
        }
        loop = asyncio.get_event_loop()
        df: DataFrame = await loop.run_in_executor(
            None, lambda: pd.read_csv(io.BytesIO(content), **csv_params)
        )
        df = df.rename(columns=self.COLUMN_MAPPING)

        # Ручное преобразование, если автоматическое не работает
        df["data_in"] = pd.to_datetime(
            df["data_in"],
            format="ISO8601",  # Альтернативный вариант для ISO-формата
            utc=True,
        )

        return df


@lru_cache()
def get_product_hs_service(
    session: AsyncSession = Depends(get_session),
) -> ProductHSService:
    repository = ProductHSRepository(session)
    return ProductHSService(repository)
