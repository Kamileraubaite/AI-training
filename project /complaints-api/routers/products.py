from fastapi import APIRouter, Depends, HTTPException

from data import PRODUCTS

router = APIRouter(prefix="/products", tags=["products"])


# Reusable lookup, like get_firms_or_404().
def get_product_or_404(product_id: str) -> dict:
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product

    raise HTTPException(status_code=404, detail="Product not found")


# Return all products, like list_firms().
@router.get("")
def list_products() -> list[dict]:
    return PRODUCTS


# Return one product, like get_firm().
@router.get("/{product_id}")
def get_product(
    product: dict = Depends(get_product_or_404),
) -> dict:
    return product