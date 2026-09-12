import os
from pathlib import Path

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional

from schemas.recommendation import RecommendationResponse
from schemas.chat import ChatRequest, ChatResponse
from services.recommendation_service import get_recommendations
from services.chat_service import process_chat_message

app = FastAPI(
    title="QuickAI — Quick Commerce Retail Intelligence Platform",
    description="AI-Driven Promotion, Inventory & Retail Intelligence for Quick Commerce",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS (keep for dev, harmless in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------- API Routes ---------------

@app.get("/api/health")
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
    """Returns AI-generated promotion and inventory recommendations."""
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
    """Handles natural language queries about inventory and recommendations."""
    try:
        return process_chat_message(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat generation failed: {str(e)}")

@app.get("/inventory")
def get_inventory():
    """Returns basic inventory aggregates."""
    recs = get_recommendations()
    return {"total_items": len(recs), "items": recs}

@app.get("/promotions")
def get_promotions():
    """Returns only items that are recommended for promotion."""
    recs = get_recommendations()
    return [r for r in recs if "PROMOTE" in r.recommendation.action]

# --------------- Serve React Frontend ---------------

# Path to the built React dashboard
FRONTEND_DIR = Path(__file__).parent.parent / "dashboard" / "dist"

if FRONTEND_DIR.is_dir():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="static-assets")

    # Serve any other static files in dist root (favicon, etc.)
    @app.get("/favicon.svg")
    @app.get("/favicon.ico")
    async def favicon():
        fav = FRONTEND_DIR / "favicon.svg"
        if fav.exists():
            return FileResponse(str(fav))
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    # Catch-all: serve index.html for any non-API route (React Router handles client-side routing)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # If a real file exists in dist, serve it
        file_path = FRONTEND_DIR / full_path
        if full_path and file_path.is_file():
            return FileResponse(str(file_path))
        # Otherwise serve index.html for React Router
        return FileResponse(str(FRONTEND_DIR / "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
