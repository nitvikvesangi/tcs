from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from schemas.recommendation import RecommendationResponse
from schemas.chat import ChatRequest, ChatResponse
from services.recommendation_service import get_recommendations
from services.chat_service import process_chat_message

app = FastAPI(
    title="QuickAI API",
    description="Backend API for Quick-Commerce Promotion & Inventory Planner",
    version="1.0.0"
)

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "backend_version": "1.0.0"}

@app.get("/recommendations", response_model=List[RecommendationResponse])
def get_recommendations_endpoint(
    city: Optional[str] = None,
    dark_store_id: Optional[str] = None,
    category: Optional[str] = None,
    demand_status: Optional[str] = None,
    search_query: Optional[str] = None,
):
    """
    Returns AI-generated promotion and inventory recommendations based on current data.
    """
    filters = {}
    if city: filters["city"] = city
    if dark_store_id: filters["dark_store_id"] = dark_store_id
    if category: filters["category"] = category
    if demand_status: filters["demand_status"] = demand_status
    if search_query: filters["search_query"] = search_query
    
    try:
        recommendations = get_recommendations(filters)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Handles natural language queries about the inventory and recommendations.
    """
    try:
        return process_chat_message(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {str(e)}")

# Add stub endpoints for inventory and promotions for clean integration
@app.get("/inventory")
def get_inventory():
    """Returns basic inventory aggregates, can be expanded later."""
    recs = get_recommendations()
    return {"total_items": len(recs), "items": recs}

@app.get("/promotions")
def get_promotions():
    """Returns only items that are recommended for promotion."""
    recs = get_recommendations()
    return [r for r in recs if "PROMOTE" in r.recommendation.action]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.1", port=8000, reload=True)
