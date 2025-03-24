from abc import ABC, abstractmethod
from functools import lru_cache
from http import HTTPStatus

from fastapi import Depends, HTTPException
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.api_models.products import Product as ProductScheme
from api.v1.api_models.products import ProductPutch
from db.postgres import get_session
from models.entity import Product


class AbstractProductRepository(ABC):

    @abstractmethod
    async def create_product(self, product: ProductScheme) -> Product:
        """
        Метод для создания товара.
        """
        pass

    @abstractmethod
    async def get_product_by_qr(self, product_qr: str) -> Product | None:
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
        self, product_qr: str, product: ProductPutch
    ) -> Product:
        """
        Метод для обновления товара.
        """
        pass


class ProductRepository(AbstractProductRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_product(self, product: ProductScheme) -> Product:
        stmt = select(
            exists().where(
                (Product.code_mark_head == product.code_mark_head)
                | (Product.name == product.name)
            )
        )
        result = await self.session.execute(stmt)
        is_duplicate = result.scalar()
        if is_duplicate:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="QR или name уще существует",
            )

        new_product = Product(**product.model_dump())
        self.session.add(new_product)
        await self.session.commit()
        await self.session.refresh(new_product)

        return new_product

    async def get_product_by_qr(self, product_qr: str) -> Product | None:
        result = await self.session.execute(
            select(Product).filter(Product.code_mark_head == product_qr)
        )
        product = result.scalar_one_or_none()
        if not product:
            return None
        return product  # type: ignore

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
        self, product_qr: str, product: ProductPutch
    ) -> Product:
        result = await self.session.execute(
            select(Product).filter(Product.code_mark_head == product_qr)
        )
        priduct_upd = result.scalar_one_or_none()
        if not priduct_upd:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="Товар не найден"
            )
        update_data = product.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(priduct_upd, key, value)

        await self.session.commit()
        await self.session.refresh(priduct_upd)
        return priduct_upd  # type: ignore


class ProductService:
    def __init__(self, repository: AbstractProductRepository):
        self.repository = repository

    async def get_product_by_qr(self, product_qr: str) -> Product | None:
        return await self.repository.get_product_by_qr(product_qr)

    async def create_product(self, product: ProductScheme) -> Product:
        return await self.repository.create_product(product)

    async def del_product_by_qr(self, product_qr: str) -> None:
        await self.repository.del_product_by_qr(product_qr)

    async def update_product(
        self, product_qr: str, product: ProductPutch
    ) -> Product:
        return await self.repository.update_product(product_qr, product)


@lru_cache()
def get_product_service(
    session: AsyncSession = Depends(get_session),
) -> ProductService:
    repository = ProductRepository(session)
    return ProductService(repository)
