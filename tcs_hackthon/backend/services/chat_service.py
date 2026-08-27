from schemas.chat import ChatRequest, ChatResponse
from services.recommendation_service import get_recommendations

def process_chat_message(request: ChatRequest) -> ChatResponse:
    query = request.message.lower()
    
    # Apply context filters if they exist
    filters = {}
    if request.context:
        if request.context.city:
            filters["city"] = request.context.city
        if request.context.dark_store_id:
            filters["dark_store_id"] = request.context.dark_store_id
            
    recs = get_recommendations(filters)
    
    if "promote" in query or "promotion" in query:
        promote_recs = [r for r in recs if "PROMOTE" in r.recommendation.action]
        product_ids = [r.product_id for r in promote_recs[:3]]
        answer = f"I found {len(promote_recs)} products recommended for promotion. Here are the top ones."
    elif "stock" in query or "inventory" in query:
        stock_recs = sorted(recs, key=lambda x: x.stockout_risk_pct, reverse=True)
        product_ids = [r.product_id for r in stock_recs[:3]]
        answer = "Here are the items with the highest stockout risk right now."
    elif "expiry" in query or "spoil" in query or "waste" in query:
        expiry_recs = sorted([r for r in recs if r.days_to_expiry < 30], key=lambda x: x.days_to_expiry)
        product_ids = [r.product_id for r in expiry_recs[:3]]
        answer = f"I found {len(expiry_recs)} products nearing expiry. We should prioritize these."
    else:
        product_ids = [r.product_id for r in recs[:3]]
        answer = "Here is an overview of the current recommendations based on your query."
        
    return ChatResponse(
        answer=answer,
        product_ids=product_ids,
        recommendations=[] # Omitted to keep payload small, frontend can cross-reference by ID
    )
