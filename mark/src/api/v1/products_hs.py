from fastapi import APIRouter, Depends, File, UploadFile

from api.v1.api_models.products_hs import ProductCheck
from core.logger import logger
from services.products_hs import ProductHSService, get_product_hs_service

producths_router = APIRouter()


@producths_router.post(
    "/upload-zip/",
    summary="load zip file",
    description="Load informations from HS.",
)  # type: ignore
async def upload_zip(
    file_hs: UploadFile = File(...),
    product_hs_service: ProductHSService = Depends(get_product_hs_service),
) -> dict[str, str | int]:
    csv_content = await product_hs_service.get_csv_from_zip(file_hs)
    df = await product_hs_service.process_csv(csv_content)
    await product_hs_service.load_data(df)
    logger.info(f"load {len(df)}")
    return {"status": "success", "processed": len(df)}


@producths_router.delete(
    "/",
    summary="delete all from table",
    description="Delete everything from the table.",
)  # type: ignore
async def clear(
    product_hs_service: ProductHSService = Depends(get_product_hs_service),
) -> dict[str, str]:
    await product_hs_service.clear()
    logger.info("clear table")
    return {"status": "success"}


@producths_router.get(
    "/check/",
    summary="check data",
    description="Data reconciliation between the HS and the database.",
)  # type: ignore
async def check(
    key: str,
    product_hs_service: ProductHSService = Depends(get_product_hs_service),
) -> list[ProductCheck]:
    difference = await product_hs_service.check(key)
    if difference:
        diff: list[dict[str, str]] = [
            {
                **(
                    {"name": pr.name, "code_mark_head": pr.code_mark_head}
                    if pr
                    else {}
                ),
                **(
                    {
                        "name_hs": pr2.name,
                        "code_mark_head_hs": pr2.code_mark_head,
                    }
                    if pr2
                    else {}
                ),
            }
            for pr, pr2 in difference
        ]
        logger.info("check table")
        return [ProductCheck(**prod_check) for prod_check in diff]
    return []
