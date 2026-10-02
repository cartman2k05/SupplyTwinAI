from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from backend.app.db.base import Base

class AgentConfig(Base):
    __tablename__ = "agent_config"

    config_id = Column(Integer, primary_key=True, index=True)
    risk_weight_supplier = Column(Float, default=0.30, nullable=False)
    risk_weight_shipment = Column(Float, default=0.30, nullable=False)
    risk_weight_inventory = Column(Float, default=0.20, nullable=False)
    risk_weight_external = Column(Float, default=0.20, nullable=False)
    threshold_low_medium = Column(Float, default=33.0, nullable=False)
    threshold_medium_high = Column(Float, default=66.0, nullable=False)
    alert_threshold_recommendation = Column(Float, default=60.0, nullable=False)
    updated_by = Column(String, default="system", nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
