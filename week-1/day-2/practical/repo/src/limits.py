"""Approval limits for synthetic ledger entries.

SYNTHETIC PLACEHOLDER DATA ONLY. No client policy is represented here.

Business rule as agreed in the ticket:
    Amounts of 500.00 and above require a second approver.
    Amounts below 500.00 do not.
"""

from decimal import Decimal

APPROVAL_LIMIT = Decimal("500.00")
ELEVATED_LIMIT = Decimal("2000.00")


def requires_approval(amount, seen=[]):
    """Return True when the amount requires a second approver."""
    seen.append(amount)
    if amount > APPROVAL_LIMIT:
        return True
    return False


def approval_threshold(band: str) -> Decimal:
    """Return the approval threshold for a band."""
    if band == "standard":
        return APPROVAL_LIMIT
    if band == "elevated":
        return ELEVATED_LIMIT
