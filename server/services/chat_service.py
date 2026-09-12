"""
Chat service — uses Groq LLM with real inventory data as context
to give intelligent, data-driven answers about promotions and inventory.
"""

import os
import json

from schemas.chat import ChatRequest, ChatResponse
from services.recommendation_service import get_recommendations


GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

SYSTEM_PROMPT = """\
You are QuickAI, an intelligent retail assistant for a quick-commerce platform.
You have access to real-time inventory and promotion recommendation data.

Your job:
- Answer questions about products, inventory, stockouts, promotions, expiry, demand trends
- Reference SPECIFIC product names, numbers, and store IDs from the data
- Be concise but data-driven — cite actual numbers (stock levels, days to expiry, discount %, risk %)
- Format key info with **bold** for emphasis
- When listing products, use bullet points
- If the user asks something unrelated to inventory/commerce, politely redirect

Keep answers under 200 words. Be direct and useful like a smart store manager.
"""


def _build_data_summary(filters: dict = None) -> str:
    """Build a concise data summary for the LLM context."""
    recs = get_recommendations(filters)
    if not recs:
        return "No products found matching the current filters."

    promote = [r for r in recs if "PROMOTE" in r.recommendation.action]
    clearance = [r for r in recs if "CLEARANCE" in r.recommendation.action]
    stockout_risk = [r for r in recs if r.stockout_risk_pct > 30]
    near_expiry = [r for r in recs if r.days_to_expiry < 7]
    overstock = [r for r in recs if r.risk_flag and "overstock" in r.risk_flag.lower()]

    lines = [
        f"Total products: {len(recs)}",
        f"Products to promote: {len(promote)}",
        f"Clearance needed: {len(clearance)}",
        f"Stockout risk (>30%): {len(stockout_risk)}",
        f"Near expiry (<7 days): {len(near_expiry)}",
        f"Overstocked: {len(overstock)}",
        "",
        "=== TOP PROMOTION CANDIDATES ===",
    ]
    for r in promote[:5]:
        lines.append(
            f"- {r.product_name} ({r.product_id}) @ {r.dark_store_id} | "
            f"Stock: {r.current_stock}, Expiry: {r.days_to_expiry}d, "
            f"Discount: {r.recommendation.discount_pct}%, "
            f"Risk: {r.risk_flag} | Reasons: {'; '.join(r.reasons[:2])}"
        )

    if stockout_risk:
        lines.append("")
        lines.append("=== STOCKOUT RISK ===")
        for r in sorted(stockout_risk, key=lambda x: x.stockout_risk_pct, reverse=True)[:5]:
            lines.append(
                f"- {r.product_name} ({r.product_id}) @ {r.dark_store_id} | "
                f"Stock: {r.current_stock}, Stockout Risk: {r.stockout_risk_pct}%, "
                f"Demand: {r.demand_status} ({r.demand_trend_pct:+.1f}%)"
            )

    if near_expiry:
        lines.append("")
        lines.append("=== NEAR EXPIRY ===")
        for r in sorted(near_expiry, key=lambda x: x.days_to_expiry)[:5]:
            lines.append(
                f"- {r.product_name} ({r.product_id}) @ {r.dark_store_id} | "
                f"Expires in {r.days_to_expiry}d, Stock: {r.current_stock}"
            )

    if overstock:
        lines.append("")
        lines.append("=== OVERSTOCKED ===")
        for r in overstock[:5]:
            lines.append(
                f"- {r.product_name} ({r.product_id}) @ {r.dark_store_id} | "
                f"Stock: {r.current_stock}, {r.risk_flag}"
            )

    # Add all product details for reference
    lines.append("")
    lines.append("=== ALL PRODUCTS (summary) ===")
    for r in recs:
        lines.append(
            f"- {r.product_name} | {r.city} {r.dark_store_id} | "
            f"Action: {r.recommendation.action} | Stock: {r.current_stock} | "
            f"Expiry: {r.days_to_expiry}d | Demand: {r.demand_status} | "
            f"Stockout Risk: {r.stockout_risk_pct}%"
        )

    return "\n".join(lines)


def _call_groq(messages: list) -> str:
    """Call Groq LLM."""
    from groq import Groq

    client = Groq(api_key=GROQ_API_KEY, timeout=15.0)
    resp = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=messages,
        temperature=0.3,
        max_tokens=500,
    )
    return resp.choices[0].message.content


def process_chat_message(request: ChatRequest) -> ChatResponse:
    """Process chat with real AI using inventory data as context."""
    query = request.message

    # Build filters from context
    filters = {}
    if request.context:
        if request.context.city:
            filters["city"] = request.context.city
        if request.context.dark_store_id:
            filters["dark_store_id"] = request.context.dark_store_id

    # Get real data
    recs = get_recommendations(filters)
    data_summary = _build_data_summary(filters)

    # If no Groq key, fall back to smart keyword matching
    if not GROQ_API_KEY:
        return _fallback_response(query, recs)

    # Call the LLM with real data context
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Here is the current inventory and recommendation data:\n\n"
                    f"{data_summary}\n\n"
                    f"User question: {query}"
                ),
            },
        ]
        answer = _call_groq(messages)

        # Extract relevant product IDs based on the query
        product_ids = _extract_relevant_ids(query, recs)

        return ChatResponse(
            answer=answer,
            product_ids=product_ids,
            recommendations=[],
        )
    except Exception as e:
        print(f"Groq API error: {e}")
        return _fallback_response(query, recs)


def _extract_relevant_ids(query: str, recs) -> list:
    """Extract the most relevant product IDs for the query."""
    q = query.lower()
    if "promote" in q or "promotion" in q or "discount" in q:
        return [r.product_id for r in recs if "PROMOTE" in r.recommendation.action][:5]
    elif "stock" in q or "inventory" in q or "stockout" in q:
        return [r.product_id for r in sorted(recs, key=lambda x: x.stockout_risk_pct, reverse=True)][:5]
    elif "expir" in q or "spoil" in q or "waste" in q:
        return [r.product_id for r in sorted(recs, key=lambda x: x.days_to_expiry) if r.days_to_expiry < 30][:5]
    elif "clearance" in q:
        return [r.product_id for r in recs if "CLEARANCE" in r.recommendation.action][:5]
    else:
        return [r.product_id for r in recs[:5]]


def _fallback_response(query: str, recs) -> ChatResponse:
    """Keyword-based fallback when no LLM is available."""
    q = query.lower()

    if "promote" in q or "promotion" in q:
        promote_recs = [r for r in recs if "PROMOTE" in r.recommendation.action]
        products = "\n".join(
            f"• **{r.product_name}** @ {r.dark_store_id} — {r.recommendation.discount_pct}% discount recommended"
            for r in promote_recs[:5]
        )
        answer = f"Found **{len(promote_recs)}** products to promote:\n\n{products}" if promote_recs else "No products currently recommended for promotion."
        product_ids = [r.product_id for r in promote_recs[:5]]
    elif "stock" in q or "inventory" in q:
        risk_recs = sorted(recs, key=lambda x: x.stockout_risk_pct, reverse=True)[:5]
        products = "\n".join(
            f"• **{r.product_name}** @ {r.dark_store_id} — {r.stockout_risk_pct}% stockout risk, {r.current_stock} units left"
            for r in risk_recs
        )
        answer = f"Top stockout risks:\n\n{products}"
        product_ids = [r.product_id for r in risk_recs]
    elif "expir" in q or "spoil" in q:
        exp_recs = sorted([r for r in recs if r.days_to_expiry < 30], key=lambda x: x.days_to_expiry)[:5]
        products = "\n".join(
            f"• **{r.product_name}** @ {r.dark_store_id} — expires in **{r.days_to_expiry} days**, {r.current_stock} units"
            for r in exp_recs
        )
        answer = f"Found **{len(exp_recs)}** products nearing expiry:\n\n{products}" if exp_recs else "No products are near expiry right now."
        product_ids = [r.product_id for r in exp_recs]
    else:
        answer = (
            f"I'm tracking **{len(recs)}** products. "
            f"Ask me about promotions, stockout risks, expiring products, or demand trends!"
        )
        product_ids = [r.product_id for r in recs[:3]]

    return ChatResponse(answer=answer, product_ids=product_ids, recommendations=[])
