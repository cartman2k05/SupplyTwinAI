from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.models.shipment import Shipment
from backend.app.models.user import User
from backend.app.auth.dependencies import get_current_user
from backend.app.schemas.shipment import ShipmentResponse

router = APIRouter(prefix="/shipments", tags=["Shipments"])

@router.get("/", response_model=List[ShipmentResponse])
def list_shipments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    shipments = db.query(Shipment).offset(skip).limit(limit).all()
    return shipments

@router.get("/{shipment_id}", response_model=ShipmentResponse)
def get_shipment(
    shipment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    shipment = db.query(Shipment).filter(Shipment.shipment_id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment
