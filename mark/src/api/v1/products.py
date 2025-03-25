from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from core.logger import logger
from services.products import ProductService, get_product_service

from .api_models.products import Product as ProductScheme
from .api_models.products import ProductPutch

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
    return ProductScheme.model_validate(product)  # type: ignore


@product_router.post(
    "/",
    summary="Добавить товар",
    description="Добавить товар.",
)  # type: ignore
async def create_product(
    product: ProductScheme,
    product_service: ProductService = Depends(get_product_service),
) -> ProductScheme:
    try:
        product_new = await product_service.create_product(product)
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"product not created: {e}",
        )
    logger.info(type(product))
    return ProductScheme.model_validate(product_new)  # type: ignore


@product_router.patch(
    "/{product_qr}",
    summary="Обновить товар",
    description="Обновить конкретный товар.",
)  # type: ignore
async def update_product(
    product_qr: str,
    product_data: ProductPutch,
    product_service: ProductService = Depends(get_product_service),
) -> ProductScheme:
    try:
        product = await product_service.update_product(
            product_qr, product_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"product not found: {e}",
        )
    return ProductScheme.model_validate(product)  # type: ignore
