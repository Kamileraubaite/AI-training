from fastapi import APIRouter, Depends, Header, HTTPException
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

# Reusable lookupgit push.
def get_customer_or_404(customer_id: str) -> dict:
    for customer in CUSTOMERS:
        if customer["id"] == customer_id:
            return customer

    raise HTTPException(status_code=404, detail="Customer not found")


# FastAPI runs the lookup before this endpoint.
@router.get("/{customer_id}")
def get_customer(
    customer: dict = Depends(get_customer_or_404),
) -> dict:
    return customer

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

# Replace a customer's editable fields.
@router.put("/{customer_id}")
def update_customer(
    new: CustomerCreate,
    customer: dict = Depends(get_customer_or_404),
) -> dict:
    customer.update(new.model_dump())
    return customer