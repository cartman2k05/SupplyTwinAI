from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from backend.app.db.base import Base

class AgentOutput(Base):
    __tablename__ = "agent_outputs"

    output_id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, index=True, nullable=False)
    entity_global_id = Column(String, index=True, nullable=False)
    output_data = Column(Text, nullable=False)
    execution_time_ms = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id = Column(Integer, primary_key=True, index=True)
    global_id = Column(String, unique=True, index=True, nullable=False)
    entity_global_id = Column(String, index=True, nullable=False)
    action_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)
    status = Column(String, default="pending", nullable=False)  # 'pending', 'accepted', 'rejected'
    reasoning_json = Column(Text, nullable=True)
    memory_citations_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class DisruptionMemory(Base):
    __tablename__ = "disruption_memory"

    memory_id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True, nullable=False)
    entity_global_id = Column(String, index=True, nullable=False)
    scenario_fingerprint = Column(String, index=True, nullable=False)
    root_cause = Column(Text, nullable=False)
    action_taken = Column(String, nullable=False)
    outcome_score = Column(Float, nullable=False)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
