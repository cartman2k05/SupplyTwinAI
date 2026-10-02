from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from backend.app.db.base import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    message_id = Column(Integer, primary_key=True, index=True)
    user_query = Column(Text, nullable=False)
    assistant_response = Column(Text, nullable=False)
    retrieved_context = Column(Text, nullable=True)  # Stored Neo4j GraphRAG facts (SRS §4.3 REQ-4)
    config_mode = Column(String, default="B", nullable=False)  # 'A' (Base LLM) or 'B' (GraphRAG)
    model_id = Column(String, nullable=False)
    latency_ms = Column(Float, nullable=False)
    is_fallback = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
