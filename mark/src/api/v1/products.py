from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from services.products import ProductService, get_product_service

from .api_models.products import Product

product_router = APIRouter()


@product_router.get(
    "/{product_qr}",
    summary="Данные по товару",
    description="Данные по конкретному товару.",
)  # type: ignore
async def fetch_product(
    product_qr: str,
    product_service: ProductService = Depends(get_product_service),
) -> Product:
    product = await product_service.get_product_by_qr(product_qr)
    if not product:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="product not found"
        )
    return Product(**product.model_dump())


@product_router.post(
    "/",
    summary="Данные по товару",
    description="Данные по конкретному товару.",
)  # type: ignore
async def create_product(
    product: Product = Depends(),
    product_service: ProductService = Depends(get_product_service),
) -> Product:
    try:
        product = await product_service.create_product(product)
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"product not created: {e}",
        )
    return Product(**product.model_dump())
