from fastapi import APIRouter, HTTPException

from data import CUSTOMERS

# Group customer endpoints under /customers.
router = APIRouter(prefix="/customers", tags=["customers"])


# Return all customer records.
@router.get("")
def list_customers() -> list[dict[str, str | bool | None]]:
    return CUSTOMERS

@router.get("/{customer_id}")
def get_customer(customer_id: str) -> dict[str, str | bool | None]:
    for customer in CUSTOMERS:
        if customer["id"] == customer_id:
            return customer

    # Return 404 if the customer does not exist.
    raise HTTPException(status_code=404, detail="Customer not found")