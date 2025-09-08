from typing import List, Optional

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .data import LISTINGS

ROOT_DIR = Path(__file__).resolve().parent.parent
app = FastAPI(title="dtar dealership API")


@app.get("/")
def root():
    return FileResponse(ROOT_DIR / "web" / "index.html")

class Listing(BaseModel):
    id: int
    make: str
    model: str
    year: int
    price: int
    mileage: int
    expected_price: int
    delta: int
    deal_score: int
    label: str


class SearchResponse(BaseModel):
    listings: List[Listing]


class AlertRequest(BaseModel):
    email: str
    make: Optional[str] = None
    model: Optional[str] = None


ALERTS: List[AlertRequest] = []


def enrich_listing(raw: dict) -> Listing:
    cohort = [
        l
        for l in LISTINGS
        if l["make"] == raw["make"]
        and l["model"] == raw["model"]
        and l["year"] == raw["year"]
    ]
    prices = [l["price"] for l in cohort]
    expected_price = int(sorted(prices)[len(prices) // 2])
    # Population standard deviation; fallback to 1 to avoid divide-by-zero
    mean_price = sum(prices) / len(prices)
    std = (sum((p - mean_price) ** 2 for p in prices) / len(prices)) ** 0.5 or 1
    delta = raw["price"] - expected_price
    z = delta / std
    score = max(0, min(100, int(50 - 10 * z)))
    if z <= -1.0:
        label = "Great"
    elif z <= -0.5:
        label = "Good"
    elif z < 0.5:
        label = "Fair"
    else:
        label = "High"
    return Listing(
        **raw,
        expected_price=expected_price,
        delta=delta,
        deal_score=score,
        label=label,
    )


@app.get("/search", response_model=SearchResponse)
def search(
    make: Optional[str] = None,
    model: Optional[str] = None,
    year: Optional[int] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_mileage: Optional[int] = None,
    max_mileage: Optional[int] = None,
) -> SearchResponse:
    results = [
        enrich_listing(l)
        for l in LISTINGS
        if (make is None or l["make"] == make)
        and (model is None or l["model"] == model)
        and (year is None or l["year"] == year)
        and (min_price is None or l["price"] >= min_price)
        and (max_price is None or l["price"] <= max_price)
        and (min_mileage is None or l["mileage"] >= min_mileage)
        and (max_mileage is None or l["mileage"] <= max_mileage)
    ]
    return SearchResponse(listings=results)


@app.get("/listing/{listing_id}", response_model=Listing)
def get_listing(listing_id: int) -> Listing:
    for l in LISTINGS:
        if l["id"] == listing_id:
            return enrich_listing(l)
    raise HTTPException(status_code=404, detail="Listing not found")


@app.post("/alerts", status_code=201)
def create_alert(alert: AlertRequest):
    ALERTS.append(alert)
    return {"status": "ok"}

