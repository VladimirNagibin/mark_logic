from fastapi import APIRouter, Depends, File, UploadFile

from core.logger import logger
from services.products_hs import ProductHSService, get_product_hs_service

producths_router = APIRouter()


@producths_router.post(
    "/upload-zip/",
    summary="load zip file",
    description="Load informations from HS.",
)  # type: ignore
async def upload_zip(
    file: UploadFile = File(...),
    product_hs_service: ProductHSService = Depends(get_product_hs_service),
) -> dict[str, str | int]:
    csv_content = await product_hs_service.get_csv_from_zip(file)
    df = await product_hs_service.process_csv(csv_content)
    await product_hs_service.load_data(df)
    logger.info(f"load {len(df)}")
    return {"status": "success", "processed": len(df)}
