"""
Chat Pydantic schemas.

Used by POST /api/v1/chat (Phase 5).
The chatbot receives a conversation history so follow-up questions work.
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ToolCallRecord(BaseModel):
    """Record of a single tool invocation made by the LLM during this turn."""
    tool_name: str
    arguments: Dict[str, Any]
    result_summary: str


class ChatRequest(BaseModel):
    """Body for POST /api/v1/chat."""
    messages: List[ChatMessage] = Field(min_length=1)
    # Optional context hints so the LLM starts with the right store/product.
    store_id: Optional[int] = None
    product_id: Optional[int] = None
    # Conversation session ID for multi-turn state (Phase 5+).
    session_id: Optional[str] = None

    model_config = {"json_schema_extra": {"example": {
        "messages": [{"role": "user", "content": "Why should I discount milk in Delhi?"}],
        "store_id": 1,
    }}}


class ChatResponse(BaseModel):
    """Response for POST /api/v1/chat."""
    response: str
    tool_calls_made: List[ToolCallRecord] = Field(default_factory=list)
    session_id: Optional[str] = None
    # If the LLM API is not configured, this flag is True and response is a
    # human-readable explanation of demo mode.
    demo_mode: bool = False
