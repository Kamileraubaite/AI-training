from decimal import Decimal

from ledger import Entry, total

BOOK = [
    Entry(reference="SYN-001", amount=Decimal("10.10")),
    Entry(reference="SYN-002", amount=Decimal("20.20")),
]


def test_total_is_exact() -> None:
    assert total(BOOK) == Decimal("30.30")
