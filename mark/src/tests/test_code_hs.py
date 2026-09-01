import pytest

from api.v1.api_models.products import ProductCodeHsCheckResult
from services.code_hs import (
    CodeHsAction,
    check_code_hs_products,
    extract_gtin_from_mark,
    resolve_code_hs,
)

MARK_HEAD = "010460123456789021SERIAL"
GTIN = "04601234567890"
GTIN13 = "4601234567890"
BAD_HS = "999"


class FakeProduct(object):
    def __init__(
        self,
        code_mark_head: str,
        code_hs: str,
        name: str = "Item",
    ) -> None:
        self.name = name
        self.code_mark_head = code_mark_head
        self.code_hs = code_hs


@pytest.mark.parametrize(  # type: ignore
    ("mark_head", "gtin"),
    [
        (MARK_HEAD, GTIN),
        ("010460123", None),
        ("XX04601234567890", None),
    ],
)
def test_extract_gtin_from_mark(mark_head: str, gtin: str | None) -> None:
    assert extract_gtin_from_mark(mark_head) == gtin


@pytest.mark.parametrize(  # type: ignore
    ("code_hs", "expected", "action", "new_value"),
    [
        ("", GTIN, CodeHsAction.FILL, GTIN),
        (GTIN, GTIN, CodeHsAction.OK, None),
        (GTIN13, GTIN, CodeHsAction.UPDATE, GTIN),
        (BAD_HS, GTIN, CodeHsAction.INCORRECT, None),
        ("123", None, CodeHsAction.INCORRECT, None),
    ],
)
def test_resolve_code_hs(
    code_hs: str,
    expected: str | None,
    action: CodeHsAction,
    new_value: str | None,
) -> None:
    assert resolve_code_hs(code_hs, expected) == (action, new_value)


def test_check_code_hs_fills_updates_and_reports() -> None:
    products = [
        FakeProduct(MARK_HEAD, ""),
        FakeProduct(MARK_HEAD, GTIN13),
        FakeProduct(MARK_HEAD, GTIN),
        FakeProduct(MARK_HEAD, BAD_HS, name="Bad"),
    ]
    check_result: ProductCodeHsCheckResult = check_code_hs_products(
        products,
    ).to_result()
    codes = [prod.code_hs for prod in products]
    mismatch = check_result.incorrect[0]

    assert codes == [GTIN, GTIN, GTIN, BAD_HS]
    assert (check_result.filled, check_result.updated) == (1, 1)
    assert (mismatch.name, mismatch.code_hs, mismatch.expected_code_hs) == (
        "Bad",
        BAD_HS,
        GTIN,
    )


def test_check_code_hs_skips_commit_when_unchanged() -> None:
    stats = check_code_hs_products([FakeProduct(MARK_HEAD, GTIN)])
    check_result = stats.to_result()

    assert (check_result.filled, check_result.updated) == (0, 0)
    assert check_result.incorrect == []
    assert stats.changed is False
