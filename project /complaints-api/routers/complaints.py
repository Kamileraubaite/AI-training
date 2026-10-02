from fastapi import APIRouter, Depends, Header, HTTPException
from models import ComplaintCreate, ComplaintUpdate
from routers.customers import get_customer_or_404
from routers.products import get_product_or_404

from data import COMPLAINTS

router = APIRouter(prefix="/complaints", tags=["complaints"])

_seen_keys: dict[str, dict] = {}

# Find a complaint or return 404.
def get_complaint_or_404(complaint_id: str) -> dict:
    for complaint in COMPLAINTS:
        if complaint["id"] == complaint_id:
            return complaint

    raise HTTPException(status_code=404, detail="Complaint not found")


# Return complaints, optionally filtered by status and theme.
@router.get("")
def list_complaints(
    status: str | None = None,
    theme: str | None = None,
) -> list[dict]:
    results = COMPLAINTS

    # Keep complaints with the requested status.
    if status is not None:
        results = [
            complaint for complaint in results
            if complaint["status"] == status
        ]

    # Keep complaints with the requested theme.
    if theme is not None:
        results = [
            complaint for complaint in results
            if complaint["theme"] == theme
        ]
    return results

# Return the complaint identified in the URL.
@router.get("/{complaint_id}")
def get_complaint(
    complaint: dict = Depends(get_complaint_or_404),
) -> dict:
    return complaint

# Record a new complaint.
@router.post("", status_code=201)
def add_complaint(new: ComplaintCreate,
    idempotency_key: str | None = Header(default=None),
) -> dict:
    # Return the previous result for a repeated request key.
    if idempotency_key is not None:
        if idempotency_key in _seen_keys:
            return _seen_keys[idempotency_key]

    # Check that the linked customer and product exist.
    get_customer_or_404(new.customer_id)
    get_product_or_404(new.product_id)

    # Generate the next complaint ID.
    new_id = max(
        (int(complaint["id"].split("-")[1]) for complaint in COMPLAINTS),
        default=0,
    ) + 1

    # New complaints start open, with no resolution details.
    complaint = {
        "id": f"CMP-{new_id:03d}",
        "customer_id": new.customer_id,
        "product_id": new.product_id,
        "description": new.description,
        "channel": new.channel,
        "received_date": new.received_date.isoformat(),
        "theme": new.theme,
        "severity": new.severity,
        "status": "open",
        "resolved_date": None,
        "resolution_summary": None,
        "outcome": None,
    }
    COMPLAINTS.append(complaint)

    # Store the result to prevent duplicate creation on retries.
    if idempotency_key is not None:
        _seen_keys[idempotency_key] = complaint
    return complaint

# Update a complaint's assessment and resolution details.
@router.put("/{complaint_id}")
def update_complaint(new: ComplaintUpdate,
    complaint: dict = Depends(get_complaint_or_404),
) -> dict:
    # Accept only the complaint statuses used by this project.
    if new.status not in ["open", "under_review", "resolved"]:
        raise HTTPException(status_code=422, detail="Invalid complaint status")

    if new.status == "resolved":
        # A resolved complaint must include its findings and outcome.
        if (
            new.resolved_date is None
            or not new.resolution_summary
            or not new.resolution_summary.strip()
            or not new.outcome
        ):
            raise HTTPException(
                status_code=422,
                detail="Resolved complaints require a date, summary and outcome",
            )

        if new.outcome not in ["upheld", "partially_upheld", "not_upheld"]:
            raise HTTPException(status_code=422, detail="Invalid complaint outcome")

        # Resolution cannot happen before the complaint was received.
        if new.resolved_date.isoformat() < complaint["received_date"]:
            raise HTTPException(
                status_code=422,
                detail="Resolution date cannot precede the received date",
            )

    elif (
        new.resolved_date is not None
        or new.resolution_summary is not None
        or new.outcome is not None
    ):
        raise HTTPException(
            status_code=422,
            detail="Unresolved complaints cannot have resolution details",
        )
    # Convert the date to text to match the existing complaint records.
    changes = new.model_dump(mode="json")
    complaint.update(changes)
    return complaint

# Delete a complaint from the in-memory records.
@router.delete("/{complaint_id}", status_code=204)
def delete_complaint(
    complaint: dict = Depends(get_complaint_or_404),
) -> None:
    COMPLAINTS.remove(complaint)