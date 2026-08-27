from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatContext(BaseModel):
    city: Optional[str] = None
    dark_store_id: Optional[str] = None
    
class ChatRequest(BaseModel):
    message: str
    context: Optional[ChatContext] = None

class ChatResponse(BaseModel):
    answer: str
    product_ids: List[str]
    recommendations: List[Dict[str, Any]] = []
