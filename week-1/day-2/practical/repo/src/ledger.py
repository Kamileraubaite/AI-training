"""Synthetic transaction ledger. SYNTHETIC PLACEHOLDER DATA ONLY."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Entry:
    reference: str
    amount: Decimal


def total(entries: Sequence[Entry]) -> Decimal:
    return sum((entry.amount for entry in entries), start=Decimal("0.00"))
