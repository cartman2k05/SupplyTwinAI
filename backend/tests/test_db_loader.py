import os
import pytest
from database.etl.db_loader import load_csv_to_postgres, SessionLocal
from backend.app.models.audit import ETLRun

def test_db_loader_and_audit_log():
    # Execute database loader
    summary = load_csv_to_postgres(v3_etl_dir="datasets/v3_etl")
    assert summary["status"] == "success"
    assert summary["counts"]["customers"] == 20652
    assert summary["counts"]["products"] == 118
    assert summary["counts"]["orders"] == 65752
    
    # Verify ETLRun audit table record
    db = SessionLocal()
    try:
        last_run = db.query(ETLRun).order_by(ETLRun.created_at.desc()).first()
        assert last_run is not None
        assert last_run.loaded_records == 180519
        assert last_run.status == "completed"
    finally:
        db.close()
