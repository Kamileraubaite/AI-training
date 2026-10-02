from fastapi import APIRouter, Depends, HTTPException

from data import COMPLAINTS

router = APIRouter(prefix="/complaints", tags=["complaints"])


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