from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatQueryRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User query message")
    config_mode: Optional[str] = Field("B", description="'A' for Base LLM, 'B' for GraphRAG")
    top_n: Optional[int] = Field(5, ge=1, le=20, description="Top-N GraphRAG fact limit")

@router.post("/query")
def process_chat_query(req: ChatQueryRequest, db: Session = Depends(get_db)):
    """Process query using LangChain Gemini RAG pipeline and store context traceability."""
    try:
        response = chat_service.process_query(
            db,
            user_query=req.message,
            config_mode=req.config_mode or "B",
            top_n=req.top_n or 5
        )
        return {"status": "success", "data": response}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat query: {str(e)}"
        )

@router.get("/history")
def get_chat_history(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve conversation history with stored Neo4j context per answer."""
    history = chat_service.get_chat_history(db, limit=limit)
    return {"status": "success", "count": len(history), "history": history}

@router.delete("/history")
def clear_chat_history(db: Session = Depends(get_db)):
    """Clear conversation history."""
    count = chat_service.clear_chat_history(db)
    return {"status": "success", "message": f"Cleared {count} chat history records."}
