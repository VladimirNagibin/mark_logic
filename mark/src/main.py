from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1.products import product_router
from core.logger import LOGGING, logger
from core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    ...
    yield
    ...


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(product_router, prefix="/api/v1/qr", tags=["qr"])


if __name__ == "__main__":
    logger.info("Start mark.")
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        log_config=LOGGING,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.APP_RELOAD,
    )
