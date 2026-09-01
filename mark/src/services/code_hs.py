from enum import Enum
from typing import Protocol, Sequence

from api.v1.api_models.products import ProductCodeHsCheckResult
from api.v1.api_models.products import ProductCodeHsMismatch
from models.entity import EMPTY

MARK_GTIN_PREFIX = "01"
GTIN_LENGTH = 14
GTIN_PAD = "0"


class CodeHsAction(str, Enum):
    FILL = "fill"
    UPDATE = "update"
    OK = "ok"
    INCORRECT = "incorrect"


class CodeHsProduct(Protocol):
    name: str
    code_mark_head: str
    code_hs: str


class CodeHsStats(object):
    def __init__(self) -> None:
        self.filled = 0
        self.updated = 0
        self.incorrect: list[ProductCodeHsMismatch] = []

    @property
    def changed(self) -> bool:
        return bool(self.filled or self.updated)

    def apply(self, action: CodeHsAction) -> None:
        if action == CodeHsAction.FILL:
            self.filled += 1
            return
        if action == CodeHsAction.UPDATE:
            self.updated += 1

    def add_mismatch(
        self,
        product: CodeHsProduct,
        expected: str | None,
    ) -> None:
        self.incorrect.append(
            ProductCodeHsMismatch(
                name=product.name,
                code_mark_head=product.code_mark_head,
                code_hs=product.code_hs,
                expected_code_hs=expected,
            )
        )

    def to_result(self) -> ProductCodeHsCheckResult:
        return ProductCodeHsCheckResult(
            filled=self.filled,
            updated=self.updated,
            incorrect=self.incorrect,
        )


def extract_gtin_from_mark(code_mark_head: str) -> str | None:
    """GTIN: drop leading 01, take the next 14 characters."""
    if not code_mark_head.startswith(MARK_GTIN_PREFIX):
        return None
    start = len(MARK_GTIN_PREFIX)
    end = start + GTIN_LENGTH
    gtin = code_mark_head[start:end]
    if len(gtin) != GTIN_LENGTH:
        return None
    return gtin


def resolve_code_hs(
    code_hs: str, expected: str | None
) -> tuple[CodeHsAction, str | None]:
    """Decide how code_hs relates to the GTIN extracted from the mark."""
    current = code_hs or EMPTY
    if expected is None:
        return CodeHsAction.INCORRECT, None
    if not current:
        return CodeHsAction.FILL, expected
    if current == expected:
        return CodeHsAction.OK, None
    if f"{GTIN_PAD}{current}" == expected:
        return CodeHsAction.UPDATE, expected
    return CodeHsAction.INCORRECT, None


def check_code_hs_products(products: Sequence[CodeHsProduct]) -> CodeHsStats:
    stats = CodeHsStats()
    for product in products:
        _sync_product_code_hs(product, stats)
    return stats


def _sync_product_code_hs(product: CodeHsProduct, stats: CodeHsStats) -> None:
    expected = extract_gtin_from_mark(product.code_mark_head)
    action, new_code_hs = resolve_code_hs(product.code_hs, expected)
    if new_code_hs is not None:
        product.code_hs = new_code_hs
        stats.apply(action)
        return
    if action == CodeHsAction.INCORRECT:
        stats.add_mismatch(product, expected)
