from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.models.warehouse import WarehouseInventory
from backend.app.models.user import User
from backend.app.auth.dependencies import get_current_user
from backend.app.schemas.inventory import InventoryResponse

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("/", response_model=List[InventoryResponse])
def list_inventory(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    inventory = db.query(WarehouseInventory).offset(skip).limit(limit).all()
    return inventory
