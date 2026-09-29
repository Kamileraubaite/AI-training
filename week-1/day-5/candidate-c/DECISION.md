Candidate A

Gate:
ruff: PASS
mypy: PASS
pytest: PASS — 3 passed

Manual cases:
exact total: Decimal('0.00'), matched=True
one penny short: Decimal('-0.01'), matched=False
empty against zero: Decimal('0.00'), matched=True

Initial finding:
No spec violation found.


Candidate B

Gate:
ruff: PASS
mypy: PASS
pytest: PASS — 3 passed

Manual checks:
exact total -> variance=Decimal('1E-14'), matched=False
one penny short -> variance=Decimal('-0.01'), matched=False
empty against zero -> variance=Decimal('0.00'), matched=True

Finding:
Reject B — violates Rule 1 because it uses float for calculations. This causes a tiny rounding error, so an exact match returns 1E-14 instead of 0.00




# Decision

**Chosen:** A

## Why

Candidate A follows all four rules in the specification.

It uses Decimal for exact arithmetic, checks for an exact zero variance,
handles an empty statement against zero correctly, and quantises the
variance to two decimal places.

The manual checks returned:

    reconcile(["38.70", "22.97", "33.32"], "94.99")
    -> variance=Decimal("0.00"), matched=True

    reconcile(["10.00", "19.99"], "30.00")
    -> variance=Decimal("-0.01"), matched=False

    reconcile([], "0.00")
    -> variance=Decimal("0.00"), matched=True


## Rejected: B

Candidate B violates Rule 1: "All arithmetic is exact. A binary float
anywhere in the calculation is a defect."

For:

    reconcile(["38.70", "22.97", "33.32"], "94.99")

it returned:

    variance=Decimal("1E-14"), matched=False

instead of:

    variance=Decimal("0.00"), matched=True

Candidate B uses float arithmetic, which introduces a rounding error.

an exactly balanced statement could incorrectly be
reported as unreconciled.


## Rejected: C

Candidate C violates Rule 2: matched is True only on an exact zero
variance, and a one-penny discrepancy is a discrepancy.

For:

    reconcile(["10.00", "19.99"], "30.00")

it returned:

    variance=Decimal("-0.01"), matched=True

instead of:

    variance=Decimal("-0.01"), matched=False

a statement that is one penny out could incorrectly be
reported as reconciled.