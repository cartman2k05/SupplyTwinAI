from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from backend.app.db.base import Base

class ETLRun(Base):
    __tablename__ = "etl_runs"

    run_id = Column(Integer, primary_key=True, index=True)
    seed = Column(Integer, nullable=False)
    raw_file_name = Column(String, nullable=False)
    loaded_records = Column(Integer, nullable=False)
    rejected_records = Column(Integer, nullable=False)
    flagged_records = Column(Integer, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    status = Column(String, default="completed", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_log"

    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    user_email = Column(String, nullable=False)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    details_json = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
