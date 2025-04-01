from fastapi import APIRouter

from core.logger import logger

health_router = APIRouter()


@health_router.get(
    "/",
    summary="check health api",
    description="Information about availability api.",
)  # type: ignore
async def check_health() -> dict[str, str]:
    logger.info("availability confirmed")
    return {"status": "OK"}
