"""Chat API route — Phase 5."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.retailer import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import chat as chat_service

router = APIRouter()


@router.post("", response_model=ChatResponse, summary="AI chatbot (demo mode if no API key)")
def chat_endpoint(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Multi-turn AI assistant. Calls real backend services for data.
    Configure GEMINI_API_KEY or OPENAI_API_KEY in .env for full LLM responses.
    Without an API key, runs in demo mode using deterministic service calls.
    """
    result = chat_service(
        db,
        messages=[m.model_dump() for m in data.messages],
        store_id=data.store_id,
        product_id=data.product_id,
    )
    return ChatResponse(
        response=result["response"],
        tool_calls_made=result.get("tool_calls_made", []),
        session_id=result.get("session_id"),
        demo_mode=result.get("demo_mode", True),
    )
