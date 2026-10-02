from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from backend.app.db.base import Base

class DisruptionEvent(Base):
    __tablename__ = "disruption_events"

    event_id = Column(Integer, primary_key=True, index=True)
    global_id = Column(String, unique=True, index=True, nullable=False)
    scenario_id = Column(String, nullable=True, index=True)
    event_type = Column(String, nullable=False)
    severity = Column(Float, nullable=False)
    target_global_id = Column(String, nullable=False)
    acceptable_action_class = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String, default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class ExternalSignal(Base):
    __tablename__ = "external_signals"

    signal_id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)  # 'Open-Meteo' or 'NewsAPI'
    signal_type = Column(String, nullable=False)
    headline = Column(String, nullable=False)
    raw_data = Column(Text, nullable=True)
    severity = Column(Float, nullable=False)
    matched_global_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
