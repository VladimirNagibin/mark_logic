from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI

from api.v1.products import product_router
from services.products import ProductService, get_product_service


def get_test_app(mock_service: ProductService) -> FastAPI:
    app = FastAPI()
    app.dependency_overrides[get_product_service] = lambda: mock_service
    app.include_router(product_router)
    return app


@pytest.fixture  # type: ignore[misc]
def mock_product_service() -> Generator[MagicMock, Any, None]:
    mock = MagicMock(spec=ProductService)
    mock.get_product_by_qr = AsyncMock()
    mock.create_product = AsyncMock()
    mock.update_product = AsyncMock()
    return mock
