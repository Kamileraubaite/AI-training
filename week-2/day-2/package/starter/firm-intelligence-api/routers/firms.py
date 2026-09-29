from fastapi import Depends, APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from data import FIRMS


router = APIRouter(prefix="/firms", tags=["firms"])

_seen_keys: dict[str, dict] ={}

# First, we need to describe what you will accept (shape)
class NewFirm(BaseModel):
    # Name, jurisdiction, revenue_usd_m, lawyers, equity_partners
    name: str = Field(min_length=1)
    jurisdiction: str = Field(min_length=2, max_length=5)
    revenue_usd_m: float = Field(gt=0)
    lawyers: int = Field(gt=0)
    equity_partners: int = Field(gt=0)

# A parameter annotated with a Pydantic model means body
# a plain int or str means a URL or query parameter


def get_firms_or_404(firm_id: int) -> dict:
    for firm in FIRMS:
        if firm["id"] == firm_id:
            return firm
    raise HTTPException(status_code=404, detail=f"Firm not found")    

    
@router.get("/health")
def health():
     return {"status": "ok"}

# list_firms always returns everything
# add two optional query parameters (not a path parameter)
# choose two of the parameters

@router.get("")
def list_firms(min_lawyers: int | None = None,
               min_revenue: float | None = None):

    firms = FIRMS

    if min_lawyers is not None:
        firms = [firm for firm in firms if firm["lawyers"] >= min_lawyers]

    if min_revenue is not None:
        firms = [firm for firm in firms if firm["revenue_usd_m"] >= min_revenue]
    # Placeholder for getting firms data
    return firms


# get one firm
# someone asks for firm 999
# return 404 

@router.get("/{firm_id}")
def get_firm(firm: dict = Depends(get_firms_or_404)):
    return firm

@router.get("/{firm_id}/benchmarks")
def get_firm_benchmarks(firm: dict = Depends(get_firms_or_404)):
            revenue = firm["revenue_usd_m"]
            return {
                "id": firm["id"],
                "name": firm["name"],
                "revenue_per_lawyer_usd": round(revenue * 1_000_000 / firm["lawyers"]),
                "revenue_per_equity_partner": round(revenue * 1_000_000 * 0.35 / firm["equity_partners"])
            }

# 200 {"id": 2, "name": "Marchetti Ruiz", "revenue_per_lawyer_usd": 1241667, "profit_per_equity_partner": 3067647}
# 404 {"detail": "No firm with id 20"}



# everything so far has been read-only... now somebody sends you data and you have no idea what it is

# Post
# /firms
@router.post("", status_code=201)
def add_firm(new: NewFirm, idempotency_key: str | None = Header(default=None)):
    if idempotency_key is not None:
        if idempotency_key in _seen_keys:
            return _seen_keys[idempotency_key]
    new_id = max(firm["id"] for firm in FIRMS) + 1
    firm = {
        "id": new_id,
        "name": new.name,
        "jurisdiction": new.jurisdiction,
        "revenue_usd_m": new.revenue_usd_m,
        "lawyers": new.lawyers,
        "equity_partners": new.equity_partners
    }
    FIRMS.append(firm)
    if idempotency_key is not None:
        _seen_keys[idempotency_key] = firm
    return firm


""" @router.post("", status_code=201)
def add_firm(new: NewFirm):
    new_id = max(firm["id"] for firm in FIRMS) + 1
    firm = {
        "id": new_id,
        "name": new.name,
        "jurisdiction": new.jurisdiction,
        "revenue_usd_m": new.revenue_usd_m,
        "lawyers": new.lawyers,
        "equity_partners": new.equity_partners
    }
    FIRMS.append(firm)
    return firm """

"""CHALLENGE 1 - replace a firm's data.

    Requirements:
      - Body is validated the same way as POST /firms (how did we do this before?).
      - Update `firm`'s fields *in place* so the change persists for later
        requests (the same idea as add_firm appending to FIRMS - mutate
        the existing dict, don't just return a new one).
      - Return the updated firm.
      - Status code 200 (the default - no status_code= needed).
    """

@router.post("/{firm_id}")
def update_firm(new: NewFirm,
                firm: dict = Depends(get_firms_or_404)):
      firm.update(new.model_dump())
      return firm


''' @router.put("/{firm_id}") ----------- you could do challenge 1 this way, or the way below
def update_firm(firm_id: int, update: NewFirm):
     
    updated_firm = get_firms_or_404(firm_id)

    updated_firm["name"] = update.name
    updated_firm["jurisdiction"] = update.jurisdiction
    updated_firm["revenue_usd_m"] = update.revenue_usd_m
    updated_firm["lawyers"] = update.lawyers
    updated_firm["equity_partners"] = update.equity_partners
    
    return updated_firm '''


"""CHALLENGE 2 - remove a firm.

    Requirements:
      - `firm` is already looked up and guaranteed to exist.
      - Remove it from the FIRMS list.
      - Return nothing (a 204 response must have an empty body - a bare
        `return` is enough; FastAPI handles the rest because of
        status_code=204 above).
    """

@router.delete("/{firm_id}", status_code=204)
def delete_firm(firm: dict = Depends(get_firms_or_404)):
    FIRMS.remove(firm)
    return