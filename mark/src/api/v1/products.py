from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from api.v1.api_models.products import Product as ProductScheme
from api.v1.api_models.products import ProductPutch
from core.logger import logger
from services.products import ProductService, get_product_service

product_router = APIRouter()


@product_router.get(
    "/{product_qr}",
    summary="product information",
    description="Information about a specific product.",
)  # type: ignore
async def fetch_product(
    product_qr: str,
    product_service: ProductService = Depends(get_product_service),
) -> ProductScheme:
    product = await product_service.get_product_by_qr(product_qr)
    if not product:
        logger.error(f"Product with QR: {product_qr} not found.")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="product not found"
        )
    return ProductScheme.model_validate(product)  # type: ignore


@product_router.post(
    "/",
    summary="add product",
    description="Add a product.",
)  # type: ignore
async def create_product(
    product: ProductScheme,
    product_service: ProductService = Depends(get_product_service),
) -> ProductScheme:
    try:
        product_new = await product_service.create_product(product)
    except Exception as error:
        logger.error(f"Product : {product} not created. Error: {error}.")
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"product not created: {error}",
        )
    logger.info(f"Product : {product} created.")
    return ProductScheme.model_validate(product_new)  # type: ignore


@product_router.patch(
    "/{product_qr}",
    summary="update product",
    description="Update a specific product.",
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
    except Exception as error:
        logger.error(
            f"Product with QR: {product_qr}, data: {product_data} not updated "
            f"Error: {error}."
        )
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"product not found: {error}",
        )
    logger.info(
        f"Product with QR: {product_qr}, data: {product_data} updated."
    )
    return ProductScheme.model_validate(product)  # type: ignore
