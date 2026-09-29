# Review: add-approval-limits

## Findings

**Where:** `src/limits.py:16`
**What:** `requires_approval(amount, seen=[])` uses a mutable default argument. The `seen`
list is created once and shared across every call that doesn't pass its own.
**Class:** MACHINE
**Ask:** Replace with `seen=None`, initialise inside the function. Also: what is `seen` for?
It's appended to but never read anywhere.

**Where:** `src/limits.py:19-21`
**What:** `if amount > APPROVAL_LIMIT: return True / return False` where `return amount >
APPROVAL_LIMIT` says the same thing in one line.
**Class:** MACHINE
**Ask:** Simplify to the direct return.

**Where:** `src/limits.py:16` and `:24`
**What:** `requires_approval` has no type annotations at all. `approval_threshold` promises
`-> Decimal` but falls through with no return when `band` isn't `"standard"` or `"elevated"`.
**Class:** MACHINE
**Ask:** Annotate both functions. Decide what `approval_threshold` should do on an unknown
band - raise, or return a default - and make the signature say so.

**Where:** `src/limits.py:19`
**What:** The ticket says "500.00 and above" requires approval. The code uses `>`, not `>=`.
`requires_approval(Decimal("500.00"))` returns `False`. This is the one value the entire rule
is about, and it's wrong.
**Class:** HUMAN
**Ask:** Change to `>=`. This needs to block the merge on its own.

**Where:** `tests/test_limits.py:9`
**What:** `test_large_amount_requires_approval` asserts
`requires_approval(Decimal("600.00")) == requires_approval(Decimal("600.00"))` - the function
compared to itself. This cannot fail no matter what the function does.
**Class:** HUMAN
**Ask:** Rewrite to assert the actual expected value, e.g.
`assert requires_approval(Decimal("600.00")) is True`.

**Where:** `tests/test_limits.py`
**What:** No test exists at exactly 500.00, the boundary the whole rule turns on. Combined
with the finding above, the suite was never capable of catching the `>` vs `>=` bug.
**Class:** HUMAN
**Ask:** Add `test_boundary_amount_requires_approval` asserting `requires_approval(Decimal("500.00")) is True`.

**Where:** `requirements.txt`
**What:** This PR is titled "Add approval limits" and touches three files, only two of which
are about approval limits. The third silently downgrades `ruff==0.16.6` to `ruff==0.14.0`.
**Class:** HUMAN
**Ask:** Revert this file. If the downgrade is intentional, it needs its own PR and its own
justification - not a line hidden inside an unrelated change.

## Verdict

**Request changes.**

The suite is green - `3 passed` - and the code does not implement the rule in the ticket.
`requires_approval(500.00)` returns `False` when the ticket requires `True`. That alone is
blocking, independent of everything else above. The tautological test and the missing
boundary test are why nobody caught it: the suite was never actually capable of failing on
this bug. And the linter downgrade in `requirements.txt` needs pulling out and justified
separately before this merges.
