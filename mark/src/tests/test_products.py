from http import HTTPStatus
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from api.v1.api_models.products import Product as ProductScheme
from api.v1.api_models.products import ProductPutch
from models.entity import StatusEnum
from tests.conftest import get_test_app

DOC_IN_FIELD = "doc_in"


@pytest.mark.asyncio  # type: ignore[misc]
async def test_fetch_product_success(mock_product_service: MagicMock) -> None:
    # Arrange
    test_qr = "test_qr_123"
    mock_product = ProductScheme(
        code_mark_head=test_qr,
        name="Test Product",
        doc_in=DOC_IN_FIELD,
        status=StatusEnum.NOT_DEFINED,
    )

    mock_product_service.get_product_by_qr.return_value = mock_product

    # Создаем тестовое приложение с моком
    test_app = get_test_app(mock_product_service)
    client = TestClient(test_app)

    # Act
    response = client.get(f"{test_qr}")

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == mock_product.model_dump()
    mock_product_service.get_product_by_qr.assert_awaited_once_with(test_qr)


@pytest.mark.asyncio  # type: ignore[misc]
async def test_fetch_product_not_found(
    mock_product_service: MagicMock,
) -> None:
    # Arrange
    test_qr = "non_existent_qr"
    mock_product_service.get_product_by_qr.return_value = None

    # Создаем тестовое приложение с моком
    test_app = get_test_app(mock_product_service)
    client = TestClient(test_app)

    # Act
    response = client.get(f"{test_qr}")

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "product not found"}


@pytest.mark.asyncio  # type: ignore[misc]
async def test_create_product_success(mock_product_service: MagicMock) -> None:
    # Arrange
    new_product = ProductScheme(
        code_mark_head="new_qr",
        name="New Product",
        doc_in=DOC_IN_FIELD,
        status=StatusEnum.NOT_DEFINED,
    )

    mock_product_service.create_product.return_value = new_product

    # Создаем тестовое приложение с моком
    test_app = get_test_app(mock_product_service)
    client = TestClient(test_app)

    # Act
    response = client.post("", json=new_product.model_dump())

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == new_product.model_dump()
    mock_product_service.create_product.assert_awaited_once()


@pytest.mark.asyncio  # type: ignore[misc]
async def test_create_product_failure(mock_product_service: MagicMock) -> None:
    # Arrange
    not_correct_product = ProductScheme(
        code_mark_head="not_correct_qr",
        name="Not correct Product",
        doc_in=DOC_IN_FIELD,
        status=StatusEnum.NOT_DEFINED,
    )
    mock_product_service.create_product.side_effect = Exception("DB error")

    # Создаем тестовое приложение с моком
    test_app = get_test_app(mock_product_service)
    client = TestClient(test_app)

    # Act
    response = client.post("", json=not_correct_product.model_dump())

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "product not created" in response.json()["detail"]


@pytest.mark.asyncio  # type: ignore[misc]
async def test_update_product_success(mock_product_service: MagicMock) -> None:
    # Arrange
    test_data: dict[str, Any] = {
        "qr": "existing_qr",
        "update_data": ProductPutch(name="Updated Name"),
        "updated_product": ProductScheme(
            code_mark_head="existing_qr",
            name="Updated Name",
            doc_in=DOC_IN_FIELD,
            status=StatusEnum.NOT_DEFINED,
        ),
    }

    mock_product_service.update_product.return_value = test_data[
        "updated_product"
    ]

    # Act & Assert
    with TestClient(get_test_app(mock_product_service)) as client:
        response = client.patch(
            f"/{test_data['qr']}", json=test_data["update_data"].model_dump()
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json() == test_data["updated_product"].model_dump()

    mock_product_service.update_product.assert_awaited_once_with(
        test_data["qr"], test_data["update_data"]
    )


@pytest.mark.asyncio  # type: ignore[misc]
async def test_update_product_not_found(
    mock_product_service: MagicMock,
) -> None:
    # Arrange
    test_qr = "non_existent_qr"
    update_data = ProductPutch(name="Updated Name")

    mock_product_service.update_product.side_effect = Exception("DB error")

    # Создаем тестовое приложение с моком
    test_app = get_test_app(mock_product_service)
    client = TestClient(test_app)

    # Act
    response = client.patch(f"{test_qr}", json=update_data.model_dump())

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
