from fastapi import APIRouter, Depends, HTTPException

from data import COMPLAINTS

router = APIRouter(prefix="/complaints", tags=["complaints"])


# Find a complaint or return 404.
def get_complaint_or_404(complaint_id: str) -> dict:
    for complaint in COMPLAINTS:
        if complaint["id"] == complaint_id:
            return complaint

    raise HTTPException(status_code=404, detail="Complaint not found")


# Return all complaint records.
@router.get("")
def list_complaints() -> list[dict]:
    return COMPLAINTS


# Return the complaint identified in the URL.
@router.get("/{complaint_id}")
def get_complaint(
    complaint: dict = Depends(get_complaint_or_404),
) -> dict:
    return complaint