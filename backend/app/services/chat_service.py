import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.models.chat import ChatMessage
from graph_rag.chain import gemini_rag_chain

logger = logging.getLogger(__name__)

class ChatService:
    """Orchestrates AI Assistant query execution, latency timing, & answer traceability logging."""

    def process_query(
        self,
        db: Session,
        user_query: str,
        config_mode: str = "B",
        top_n: int = 5
    ) -> Dict[str, Any]:
        """Generate response via GraphRAG chain and record context in chat_messages table."""
        result = gemini_rag_chain.generate_response(user_query, config_mode=config_mode, top_n=top_n)

        # Save traceability record in database (SRS §4.3 REQ-4)
        msg_record = ChatMessage(
            user_query=user_query,
            assistant_response=result["answer"],
            retrieved_context=result["retrieved_context"],
            config_mode=result["config_mode"],
            model_id=result["model_id"],
            latency_ms=result["latency_ms"],
            is_fallback=result["is_fallback"]
        )
        db.add(msg_record)
        db.commit()
        db.refresh(msg_record)

        return {
            "message_id": msg_record.message_id,
            "user_query": msg_record.user_query,
            "assistant_response": msg_record.assistant_response,
            "retrieved_context": msg_record.retrieved_context,
            "config_mode": msg_record.config_mode,
            "model_id": msg_record.model_id,
            "latency_ms": msg_record.latency_ms,
            "is_fallback": msg_record.is_fallback,
            "created_at": msg_record.created_at.isoformat()
        }

    def get_chat_history(self, db: Session, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve historical chat records with stored context."""
        records = db.query(ChatMessage).order_by(ChatMessage.message_id.asc()).limit(limit).all()
        return [
            {
                "message_id": r.message_id,
                "user_query": r.user_query,
                "assistant_response": r.assistant_response,
                "retrieved_context": r.retrieved_context,
                "config_mode": r.config_mode,
                "model_id": r.model_id,
                "latency_ms": r.latency_ms,
                "is_fallback": r.is_fallback,
                "created_at": r.created_at.isoformat()
            }
            for r in records
        ]

    def clear_chat_history(self, db: Session) -> int:
        """Clear all chat history records."""
        count = db.query(ChatMessage).delete()
        db.commit()
        return count

chat_service = ChatService()
