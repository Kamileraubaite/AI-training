from fastapi import APIRouter, Header, HTTPException
from models import CustomerCreate

from data import CUSTOMERS

# Group customer endpoints under /customers.
router = APIRouter(prefix="/customers", tags=["customers"])

_seen_keys: dict[str, dict] = {}


# Return all customer records.
# Return customers, optionally filtered by segment and vulnerability flag.
@router.get("")
def list_customers(
segment: str | None = None,
    vulnerability_flag: bool | None = None,
) -> list[dict[str, str | bool | None]]:
    results = CUSTOMERS

    # Apply this filter only when a segment is provided.
    if segment is not None:
        results = [
            customer for customer in results
            if customer["segment"] == segment
        ]

    # Check for None so that both True and False work as filters.
    if vulnerability_flag is not None:
        results = [
            customer for customer in results
            if customer["vulnerability_flag"] == vulnerability_flag
        ]

    return results

@router.get("/{customer_id}")
def get_customer(customer_id: str) -> dict[str, str | bool | None]:
    for customer in CUSTOMERS:
        if customer["id"] == customer_id:
            return customer

    # Return 404 if the customer does not exist.
    raise HTTPException(status_code=404, detail="Customer not found")

# Post
# /customers
@router.post("", status_code=201)
def add_customer(new: CustomerCreate, idempotency_key: str | None = Header(default=None),) -> dict:
    if idempotency_key is not None:
        if idempotency_key in _seen_keys:
            return _seen_keys[idempotency_key]
    new_id = max((int(customer["id"].split("-")[1]) for customer in CUSTOMERS),default=0,) + 1
    customer = {
        "id": f"CUST-{new_id:03d}",
        "name": new.name,
        "segment": new.segment,
        "vulnerability_flag": new.vulnerability_flag,
        "support_needs": new.support_needs,
    }
    CUSTOMERS.append(customer)
    if idempotency_key is not None:
        _seen_keys[idempotency_key] = customer
    return customer