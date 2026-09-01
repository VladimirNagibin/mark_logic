from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from api.v1.api_models.products import Product as ProductScheme
from models.entity import StatusEnum
from tests.conftest import get_test_app

CODE_HS = "04601234567890"
PRODUCT_GROUP = 1


@pytest.mark.asyncio  # type: ignore
async def test_fetch_product_group_success(
    mock_product_service: MagicMock,
) -> None:
    mock_product = ProductScheme(
        code_mark_head="test_qr",
        name="Test Product",
        doc_in="doc_in",
        code_hs=CODE_HS,
        product_group=PRODUCT_GROUP,
        status=StatusEnum.NOT_DEFINED,
    )
    mock_product_service.get_product_by_code_hs.return_value = mock_product

    client = TestClient(get_test_app(mock_product_service))
    response = client.get(f"/code-hs/{CODE_HS}")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"product_group": PRODUCT_GROUP}
    mock_product_service.get_product_by_code_hs.assert_awaited_once_with(
        CODE_HS,
    )


@pytest.mark.asyncio  # type: ignore
async def test_fetch_product_group_not_found(
    mock_product_service: MagicMock,
) -> None:
    mock_product_service.get_product_by_code_hs.return_value = None

    client = TestClient(get_test_app(mock_product_service))
    response = client.get(f"/code-hs/{CODE_HS}")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "product not found"}
