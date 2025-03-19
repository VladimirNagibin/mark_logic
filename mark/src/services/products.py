from abc import ABC, abstractmethod
from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.v1.api_models.products import Product as ProductScheme
from db.postgres import get_session
from models.entity import Product

# from typing import AsyncGenerator


class AbstractProductRepository(ABC):

    @abstractmethod
    async def create_product(self, product: ProductScheme) -> Product:
        """
        Метод для создания товара.
        """
        pass

    @abstractmethod
    async def get_product_by_qr(self, product_qr: str) -> ProductScheme | None:
        """
        Метод для получения данных по товару.
        """
        pass

    @abstractmethod
    async def del_product_by_qr(self, product_qr: str) -> None:
        """
        Метод для удаления товара.
        """
        pass

    @abstractmethod
    async def update_product(
        self, product_qr: str, product: ProductScheme
    ) -> ProductScheme:
        """
        Метод для обновления товара.
        """
        pass


class ProductRepository(AbstractProductRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_product(self, product: ProductScheme) -> Product:
        existing_product = await self.session.execute(
            select(Product).filter(
                Product.code_mark_head == product.code_mark_head
            )
        )
        if existing_product.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail="QR уще существует"
            )
        new_product = Product(**product.model_dump())
        self.session.add(new_product)
        await self.session.commit()
        await self.session.refresh(new_product)

        return new_product

    async def get_product_by_qr(self, product_qr: str) -> ProductScheme | None:
        result = await self.session.execute(
            select(Product).filter(Product.code_mark_head == product_qr)
        )
        product = result.scalar_one_or_none()
        if not product:
            return None
        return ProductScheme.model_validate(product)  # type: ignore

    async def del_product_by_qr(self, product_qr: str) -> None:
        result = await self.session.execute(
            select(Product).filter(Product.code_mark_head == product_qr)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="QR не найден"
            )
        await self.session.delete(product)
        await self.session.commit()

    async def update_product(
        self, product_qr: str, product: ProductScheme
    ) -> ProductScheme:
        return product


class ProductService:
    def __init__(self, repository: AbstractProductRepository):
        self.repository = repository

    async def get_product_by_qr(self, product_qr: str) -> ProductScheme | None:
        return await self.repository.get_product_by_qr(product_qr)

    async def create_product(self, product: ProductScheme) -> ProductScheme:
        return await self.repository.create_product(product)

    async def del_product_by_qr(self, product_qr: str) -> None:
        await self.repository.del_product_by_qr(product_qr)

    async def update_product(
        self, product_qr: str, product: ProductScheme
    ) -> ProductScheme:
        return await self.repository.update_product(product_qr, product)


@lru_cache()
def get_product_service(
    session: AsyncSession = Depends(get_session),
) -> ProductService:
    repository = ProductRepository(session)
    return ProductService(repository)
