from fastapi import APIRouter

from data import CUSTOMERS

# Group customer endpoints under /customers.
router = APIRouter(prefix="/customers", tags=["customers"])


# Return all customer records.
@router.get("")
def list_customers() -> list[dict[str, str | bool | None]]:
    return CUSTOMERS
