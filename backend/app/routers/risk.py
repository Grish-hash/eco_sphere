from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Warehouse, WeatherSnapshot, User
from ..auth import get_current_user
from ..services.risk import fetch_forecast, level

router = APIRouter(prefix="/risk", tags=["risk"])


@router.post("/refresh")
def refresh(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Fetch the 7-day forecast for each warehouse and store the peak-risk day."""
    updated, failed = 0, []
    for w in db.query(Warehouse).filter(Warehouse.company_id == user.company_id).all():
        try:
            days = fetch_forecast(w.lat, w.lng)
        except Exception:
            failed.append(w.name)
            continue
        peak = max(days, key=lambda d: d["risk"])
        db.add(WeatherSnapshot(
            warehouse_id=w.id, wind_speed=peak["wind"], precipitation=peak["rain"],
            temp=peak["temp"], risk_score=peak["risk"], peak_day=peak["date"], forecast=days,
        ))
        updated += 1
    db.commit()
    return {"updated": updated, "failed": failed}


@router.get("/nodes")
def nodes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    out = []
    for w in db.query(Warehouse).filter(Warehouse.company_id == user.company_id).order_by(Warehouse.id).all():
        snap = (db.query(WeatherSnapshot).filter(WeatherSnapshot.warehouse_id == w.id)
                .order_by(WeatherSnapshot.fetched_at.desc()).first())
        out.append({
            "id": w.id, "name": w.name, "lat": w.lat, "lng": w.lng,
            "risk_score": snap.risk_score if snap else None,
            "level": level(snap.risk_score if snap else None),
            "peak_day": snap.peak_day if snap else None,
            "forecast": snap.forecast if snap else [],
        })
    return out
