import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Route, Warehouse, User
from ..schemas import RouteIn, RouteOut
from ..auth import get_current_user
from ..services.emissions import haversine_km, emissions_kg, SPEEDS

router = APIRouter(prefix="/routes", tags=["routes"])
fleet_router = APIRouter(prefix="/vehicles", tags=["fleet"])

MODES = {"truck", "rail", "ship", "air"}
SIM_SPEEDUP = 300  # demo only: makes simulated vehicles visibly move


def to_out(r: Route) -> RouteOut:
    dist = haversine_km(r.origin.lat, r.origin.lng, r.destination.lat, r.destination.lng)
    return RouteOut(
        id=r.id, origin_id=r.origin_id, destination_id=r.destination_id,
        origin_name=r.origin.name, destination_name=r.destination.name,
        origin_lat=r.origin.lat, origin_lng=r.origin.lng,
        dest_lat=r.destination.lat, dest_lng=r.destination.lng,
        transport_mode=r.transport_mode, load_tons=r.load_tons,
        distance_km=round(dist, 1),
        emissions_kg=round(emissions_kg(dist, r.load_tons, r.transport_mode), 1),
    )


def _own_routes(db: Session, user: User):
    return db.query(Route).filter(Route.company_id == user.company_id).order_by(Route.id).all()


@router.get("", response_model=list[RouteOut])
def list_routes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return [to_out(r) for r in _own_routes(db, user)]


@router.post("", response_model=RouteOut)
def create_route(body: RouteIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if body.transport_mode not in MODES:
        raise HTTPException(400, f"transport_mode must be one of {sorted(MODES)}")
    if body.origin_id == body.destination_id:
        raise HTTPException(400, "Origin and destination must differ")
    for wid in (body.origin_id, body.destination_id):
        ok = db.query(Warehouse).filter(Warehouse.id == wid, Warehouse.company_id == user.company_id).first()
        if not ok:
            raise HTTPException(404, f"Warehouse {wid} not found")
    r = Route(company_id=user.company_id, **body.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return to_out(r)


@router.get("/{rid}/emissions")
def route_emissions(rid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    r = db.query(Route).filter(Route.id == rid, Route.company_id == user.company_id).first()
    if not r:
        raise HTTPException(404, "Route not found")
    o = to_out(r)
    return {"route_id": rid, "distance_km": o.distance_km, "emissions_kg": o.emissions_kg}


@router.delete("/{rid}")
def delete_route(rid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    r = db.query(Route).filter(Route.id == rid, Route.company_id == user.company_id).first()
    if not r:
        raise HTTPException(404, "Route not found")
    db.delete(r)
    db.commit()
    return {"deleted": rid}


@fleet_router.get("")
def vehicles(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Simulated live fleet: one vehicle per route, position interpolated from the clock."""
    out = []
    for r in _own_routes(db, user):
        o = to_out(r)
        hours = max(o.distance_km / SPEEDS.get(r.transport_mode, 60), 0.1)
        elapsed_h = (time.time() * SIM_SPEEDUP / 3600) + r.id * 1.7
        progress = (elapsed_h % hours) / hours
        out.append({
            "route_id": r.id,
            "mode": r.transport_mode,
            "progress": round(progress, 3),
            "lat": o.origin_lat + (o.dest_lat - o.origin_lat) * progress,
            "lng": o.origin_lng + (o.dest_lng - o.origin_lng) * progress,
        })
    return out
