from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.models.audit import ETLRun
from backend.app.models.user import User
from backend.app.auth.dependencies import require_admin
from backend.app.schemas.etl import ETLLoadResponse, ETLRunResponse
from database.etl.db_loader import load_csv_to_postgres

router = APIRouter(prefix="/etl", tags=["ETL Management (Admin)"])

@router.post("/load", response_model=ETLLoadResponse)
def trigger_etl_load(
    v3_etl_dir: str = "datasets/v3_etl",
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    try:
        res = load_csv_to_postgres(v3_etl_dir=v3_etl_dir, db=db)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ETL Load failed: {str(e)}")

@router.get("/history", response_model=List[ETLRunResponse])
def get_etl_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    runs = db.query(ETLRun).order_by(ETLRun.created_at.desc()).offset(skip).limit(limit).all()
    return runs
