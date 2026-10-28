from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Warehouse, Route, WeatherSnapshot, User
from ..schemas import WarehouseIn, WarehouseOut
from ..auth import get_current_user

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


def _get_own(db: Session, wid: int, user: User) -> Warehouse:
    # multi-tenancy: always filter by the logged-in user's company
    w = db.query(Warehouse).filter(Warehouse.id == wid, Warehouse.company_id == user.company_id).first()
    if not w:
        raise HTTPException(404, "Warehouse not found")
    return w


@router.get("", response_model=list[WarehouseOut])
def list_warehouses(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Warehouse).filter(Warehouse.company_id == user.company_id).order_by(Warehouse.id).all()


@router.post("", response_model=WarehouseOut)
def create_warehouse(body: WarehouseIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    w = Warehouse(company_id=user.company_id, **body.model_dump())
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


@router.put("/{wid}", response_model=WarehouseOut)
def update_warehouse(wid: int, body: WarehouseIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    w = _get_own(db, wid, user)
    for k, v in body.model_dump().items():
        setattr(w, k, v)
    db.commit()
    db.refresh(w)
    return w


@router.delete("/{wid}")
def delete_warehouse(wid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    w = _get_own(db, wid, user)
    db.query(Route).filter(or_(Route.origin_id == wid, Route.destination_id == wid)).delete()
    db.query(WeatherSnapshot).filter(WeatherSnapshot.warehouse_id == wid).delete()
    db.delete(w)
    db.commit()
    return {"deleted": wid}
