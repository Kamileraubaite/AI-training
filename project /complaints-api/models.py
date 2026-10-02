from pydantic import BaseModel, Field
from datetime import date

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

# Fields required to record a new complaint.
class ComplaintCreate(BaseModel):
    customer_id: str = Field(min_length=1)
    product_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    channel: str = Field(min_length=1)
    received_date: date

    # Leave classification pending until the complaint is assessed.
    theme: str = "unclassified"
    severity: str = "unassessed"

# Fields staff provide when assessing or resolving a complaint.
class ComplaintUpdate(BaseModel):
    theme: str = Field(min_length=1)
    severity: str = Field(min_length=1)
    status: str = Field(min_length=1)
    resolved_date: date | None = None
    resolution_summary: str | None = Field(default=None, min_length=1)
    outcome: str | None = Field(default=None, min_length=1)