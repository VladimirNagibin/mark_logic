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
        Method for creating a product.
        """
        ...

    @abstractmethod
    async def get_product_by_qr(self, product_qr: str) -> Product | None:
        """
        Method for getting product data.
        """
        ...  # noqa: WPS463

    @abstractmethod
    async def del_product_by_qr(self, product_qr: str) -> None:
        """
        Method for deleting the product.
        """
        ...

    @abstractmethod
    async def update_product(
        self, product_qr: str, product: ProductPutch
    ) -> Product:
        """
        Method for updating the product.
        """
        ...


class ProductRepository(AbstractProductRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_product(self, product: ProductScheme) -> Product:
        stmt = select(
            exists().where(
                (Product.code_mark_head == product.code_mark_head)
                | (Product.name == product.name)  # noqa: W503
            )
        )
        product_result = await self.session.execute(stmt)
        is_duplicate = product_result.scalar()
        if is_duplicate:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail=(
                    f"QR: {product.code_mark_head} or name: {product.name} "
                    "still exists"
                ),
            )

        new_product = Product(**product.model_dump())
        self.session.add(new_product)
        await self.session.commit()
        await self.session.refresh(new_product)

        return new_product

    async def get_product_by_qr(self, product_qr: str) -> Product | None:
        product_result = await self.session.execute(
            select(Product).filter(Product.code_mark_head == product_qr)
        )
        product = product_result.scalar_one_or_none()
        if not product:
            return None
        return product  # type: ignore

    async def del_product_by_qr(self, product_qr: str) -> None:
        product_result = await self.session.execute(
            select(Product).filter(Product.code_mark_head == product_qr)
        )
        product = product_result.scalar_one_or_none()
        if not product:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Product with QR: {product_qr} not found",
            )
        await self.session.delete(product)
        await self.session.commit()

    async def update_product(
        self, product_qr: str, product: ProductPutch
    ) -> Product:
        product_result = await self.session.execute(
            select(Product).filter(Product.code_mark_head == product_qr)
        )
        priduct_upd = product_result.scalar_one_or_none()
        if not priduct_upd:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail=f"Product with QR: {product_qr} not found",
            )
        update_data = product.model_dump(exclude_unset=True)

        for key, attr in update_data.items():
            setattr(priduct_upd, key, attr)

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
