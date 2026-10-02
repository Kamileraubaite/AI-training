from pydantic import BaseModel, Field

# Fields required when creating a customer.
class CustomerCreate(BaseModel):
    name: str = Field(min_length=1)
    segment: str = Field(min_length=1)
    vulnerability_flag: bool = Field(default=False)
    support_needs: str | None = None

# A stored customer also has an ID
class Customer(CustomerCreate):
    id: str = Field(min_length=1)

# Fields required when creating or updating a product.
class ProductCreate(BaseModel):
    name: str = Field(min_length=1)
    product_type: str = Field(min_length=1)
    terms_document_id: str = Field(min_length=1)