from fastapi import APIRouter, Depends, Header, HTTPException

from data import PRODUCTS, COMPLAINTS
from documents import DOCUMENTS
from models import ProductCreate

router = APIRouter(prefix="/products", tags=["products"])

_seen_keys: dict[str, dict] = {}

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

# Checks that the terms document linked to a 
# product is valid before we save the product.
def get_terms_document_or_404(document_id: str) -> dict:
    for document in DOCUMENTS:
        if document["id"] == document_id:
            if document["type"] != "product_terms":
                raise HTTPException(
                    status_code=422,
                    detail="Document must contain product terms",
                )
            return document

    raise HTTPException(
        status_code=404,
        detail="Terms document not found",
    )

# Create a new banking product.
@router.post("", status_code=201)
def add_product(new: ProductCreate, 
                idempotency_key: str | None = Header(default=None),
                ) -> dict:
    # Return the previous result if this request key has already been used.
    if idempotency_key is not None:
        if idempotency_key in _seen_keys:
            return _seen_keys[idempotency_key]

    # Validate the product's linked terms document before saving.
    get_terms_document_or_404(new.terms_document_id)

    # Find the highest product number and add one.
    new_id = max(
        (int(product["id"].split("-")[1]) for product in PRODUCTS),
        default=0,
    ) + 1

    # Build the product record using the validated input.
    product = {
        "id": f"PRD-{new_id:03d}",
        "name": new.name,
        "product_type": new.product_type,
        "terms_document_id": new.terms_document_id,
    }

    # Store the product in the in-memory list.
    PRODUCTS.append(product)

    # Remember the result so a repeated request does not create a duplicate.
    if idempotency_key is not None:
        _seen_keys[idempotency_key] = product

    return product

# Replacing a product's editable fields.
@router.put("/{product_id}")
def update_product(new: ProductCreate,
    product: dict = Depends(get_product_or_404),
) -> dict:
    # Validate the linked terms document before changing the product.
    get_terms_document_or_404(new.terms_document_id)

    # Update the existing record while keeping its ID.
    product.update(new.model_dump())
    return product

# Delete a product unless complaints refer to it.
@router.delete("/{product_id}", status_code=204)
def delete_product(
    product: dict = Depends(get_product_or_404),
) -> None:
    # Preserve products that are linked to complaint records.
    for complaint in COMPLAINTS:
        if complaint["product_id"] == product["id"]:
            raise HTTPException(
                status_code=409,
                detail="Product has linked complaints and cannot be deleted",
            )

    PRODUCTS.remove(product)
    return