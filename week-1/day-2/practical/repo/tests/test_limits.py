"""Tests for approval limits. SYNTHETIC PLACEHOLDER DATA ONLY."""

from decimal import Decimal

from limits import requires_approval


def test_large_amount_requires_approval() -> None:
    assert requires_approval(Decimal("600.00")) == requires_approval(Decimal("600.00"))


def test_small_amount_does_not_require_approval() -> None:
    assert requires_approval(Decimal("10.00")) is False
