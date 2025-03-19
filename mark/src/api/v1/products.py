from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from core.logger import logger
from services.products import ProductService, get_product_service

from .api_models.products import Product as ProductScheme

product_router = APIRouter()


@product_router.get(
    "/{product_qr}",
    summary="Данные по товару",
    description="Данные по конкретному товару.",
)  # type: ignore
async def fetch_product(
    product_qr: str,
    product_service: ProductService = Depends(get_product_service),
) -> ProductScheme:
    product = await product_service.get_product_by_qr(product_qr)
    if not product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="product not found"
        )
    return ProductScheme(**product.model_dump())


@product_router.post(
    "/",
    summary="Добавить товар",
    description="Добавить товар.",
)  # type: ignore
async def create_product(
    product: ProductScheme = Depends(),
    product_service: ProductService = Depends(get_product_service),
) -> ProductScheme:
    try:
        product = await product_service.create_product(product)
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"product not created: {e}",
        )
    logger.info(type(product))
    return ProductScheme.model_validate(product)  # type: ignore
