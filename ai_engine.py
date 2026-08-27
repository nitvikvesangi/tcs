"""
ai_engine.py — AI/Chat Engine for Quick Commerce Promotion Planner
==================================================================================
Converts structured output from inventory_engine + promotion_engine into
natural-language explanations and risk flags via Groq LLM API.

ARCHITECTURAL RULE: The LLM never does math. It only translates pre-computed
numbers into words. All analytics happen upstream in the engines.

Functions:
    generate_explanation(product_row) → str   — natural-language reasoning
    generate_risk_flag(product_row)   → str | None — dark-store risk warning

Usage:
    export GROQ_API_KEY="your-key"
    python ai_engine.py          # runs built-in tests on sample rows
"""

from __future__ import annotations

import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file (picks up NVIDIA_API_KEY automatically)
load_dotenv()

# ---------------------------------------------------------------------------
# Config — Dual-Provider: NVIDIA NIM (Llama 90B / Nemotron) + Groq Fallback
# ---------------------------------------------------------------------------
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_PRIMARY_MODEL = "meta/llama-3.2-11b-vision-instruct"
NVIDIA_FALLBACK_MODEL = "nvidia/nemotron-3-super-120b-a12b"
GROQ_MODEL = "qwen/qwen3.8-27b"

LLM_TEMPERATURE = 0.3          # low temp → deterministic, factual tone
LLM_MAX_TOKENS = 512
REQUEST_TIMEOUT = 4.0          # seconds per request before fallback

def _call_llm(messages: list, temperature: float = LLM_TEMPERATURE, max_tokens: int = LLM_MAX_TOKENS) -> str:
    """
    Call LLM with resilient dual-provider fallback:
    1. Try NVIDIA NIM (Llama 3.2 90B / Nemotron)
    2. Fall back to Groq (ultra-fast 0.3s response) if NVIDIA times out or fails
    """
    nvidia_key = os.environ.get("NVIDIA_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")

    # Strategy 1: Try NVIDIA NIM if key is present
    if nvidia_key:
        try:
            from openai import OpenAI
            client = OpenAI(base_url=NVIDIA_BASE_URL, api_key=nvidia_key, timeout=REQUEST_TIMEOUT)
            for model in [NVIDIA_PRIMARY_MODEL, NVIDIA_FALLBACK_MODEL]:
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        timeout=REQUEST_TIMEOUT,
                    )
                    raw = response.choices[0].message.content.strip()
                    clean = _strip_thinking(raw)
                    if clean:
                        return clean
                except Exception as e:
                    # Model not found, timeout, or overloaded, try next
                    continue
        except Exception as e:
            pass

    # Strategy 2: Fall back to Groq
    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key, timeout=REQUEST_TIMEOUT)
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=REQUEST_TIMEOUT,
            )
            raw = response.choices[0].message.content.strip()
            return _strip_thinking(raw)
        except Exception as e:
            raise RuntimeError(f"Groq API error: {e}")

    raise RuntimeError(
        "No working LLM provider found. Please set NVIDIA_API_KEY or GROQ_API_KEY in .env"
    )


def _strip_thinking(text: str) -> str:
    """Extract clean answer from reasoning model output.
    Looks for <response>...</response> tags first, then falls back to
    stripping <think> blocks and reasoning traces."""
    import re
    # Strategy 1: Extract from <response> tags (our prompts ask for this)
    match = re.search(r'<response>(.*?)</response>', text, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    # Strategy 2: Remove <think>...</think> blocks
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    # Strategy 3: Remove numbered reasoning lines ("1. condition...", "2. ...") 
    lines = text.split('\n')
    clean_lines = []
    for line in lines:
        s = line.strip().lower()
        # Skip lines that look like reasoning/evaluation
        if any(marker in s for marker in [
            'sentence1:', 'sentence2:', 'sentence3:', 'sentence4:',
            'let\'s craft', 'let\'s count', 'total ~', 'total maybe',
            'check numbers', 'word count', 'make sure not to invent',
            'we need to check', 'we need to evaluate', 'we need to produce',
            'so condition', 'so no.', 'so not.', 'condition true',
            'condition not met', 'not defined explicitly', 'need to define',
            'need to infer', 'count words', 'under 100', 'all from json',
            'that\'s', 'words.',
        ]):
            continue
        # Skip numbered condition checks like "1. Expiry within..." "2. Stockout..."
        if re.match(r'^\d+\.\s+(expiry|stockout|competitor|negative|stock turnover)', s):
            continue
        # Skip lines with evaluation fragments
        if re.match(r'^-?\s*(days_to_expiry|stockout_risk|competitor_price|negative_review|stock_turnover)', s):
            continue
        clean_lines.append(line)
    result = '\n'.join(clean_lines).strip()
    return result if result else text


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

EXPLANATION_SYSTEM_PROMPT = """\
You are a concise retail analytics assistant for a Quick Commerce dark-store network.

Your job: given a structured recommendation (JSON), produce a 3-5 sentence
explanation a store manager can understand in 10 seconds. Cover:
1. WHY this action was recommended (the key data signals)
2. WHAT the recommended discount/action is
3. The trade-offs between the 2-3 options provided (profit vs clearance speed)

Rules:
- Never invent numbers. Only reference numbers from the JSON provided.
- Be specific: mention product name, store ID, exact percentages.
- Use plain business English, no jargon.
- If the action is NO PROMOTION, explain why restraint is the right call.
- Keep it under 100 words.

You MUST wrap your final answer inside <response></response> tags. Example:
<response>Your explanation here.</response>
"""

RISK_FLAG_SYSTEM_PROMPT = """\
You are a retail risk analyst for Quick Commerce dark stores.

Task:
Analyze the product JSON and determine if an urgent dark-store operational risk exists:
1. Imminent Expiry Waste: days_to_expiry <= 2 days and current_stock > minimum_stock
2. Imminent Stockout: stockout_risk_pct > 60% with rising demand
3. Customer Churn: competitor_price_gap_pct > 20% with 0% current discount
4. Quality Dead-Stock: negative_review_rate > 0.35 with existing inventory

Instructions:
- If a risk is present, output a 1-sentence warning stating the store ID, product name, and the specific risk metric.
- If no risk is present, output: NO_RISK
- Wrap your final response inside <response></response> tags.
"""


def _build_explanation_prompt(product_row: dict) -> str:
    """Build the user message for explanation generation."""
    # Extract only the fields the LLM needs (avoid leaking irrelevant data)
    context = {
        "product_id": product_row.get("product_id"),
        "product_name": product_row.get("product_name"),
        "dark_store_id": product_row.get("dark_store_id"),
        "category": product_row.get("category"),
        "recommended_action": product_row.get("recommended_action"),
        "discount_pct": product_row.get("discount_pct"),
        "objective_used": product_row.get("objective_used"),
        "reasons": product_row.get("reasons", []),
        "risk_flag": product_row.get("risk_flag"),
        "inventory_snapshot": product_row.get("inventory_snapshot", {}),
        "options": product_row.get("options", []),
        "chosen_option": product_row.get("chosen_option", {}),
        # Additional context fields (from raw CSV row, if present)
        "mrp": product_row.get("mrp"),
        "unit_price": product_row.get("unit_price"),
        "demand_trend_pct": product_row.get("demand_trend_pct"),
        "competitor_price_gap_pct": product_row.get("competitor_price_gap_pct"),
        "product_rating": product_row.get("product_rating"),
        "sales_7d": product_row.get("sales_7d"),
    }
    return f"Generate explanation for this recommendation:\n```json\n{json.dumps(context, indent=2, default=str)}\n```"


def _build_risk_prompt(product_row: dict) -> str:
    """Build the user message for risk flag generation."""
    context = {
        "product_id": product_row.get("product_id"),
        "product_name": product_row.get("product_name"),
        "dark_store_id": product_row.get("dark_store_id"),
        "category": product_row.get("category"),
        "current_stock": product_row.get("current_stock"),
        "minimum_stock": product_row.get("minimum_stock"),
        "maximum_stock": product_row.get("maximum_stock"),
        "days_to_expiry": product_row.get("days_to_expiry"),
        "shelf_life_days": product_row.get("shelf_life_days"),
        "stock_turnover_days": product_row.get("stock_turnover_days"),
        "stockout_risk_pct": product_row.get("stockout_risk_pct"),
        "demand_trend_pct": product_row.get("demand_trend_pct"),
        "demand_status": product_row.get("demand_status"),
        "competitor_price_gap_pct": product_row.get("competitor_price_gap_pct"),
        "competitor_discount_pct": product_row.get("competitor_discount_pct"),
        "current_discount_pct": product_row.get("current_discount_pct"),
        "negative_review_rate": product_row.get("negative_review_rate"),
        "product_rating": product_row.get("product_rating"),
        "sales_7d": product_row.get("sales_7d"),
        "sales_30d": product_row.get("sales_30d"),
        # Include inventory snapshot if available (from engine output)
        "inventory_snapshot": product_row.get("inventory_snapshot", {}),
        "recommended_action": product_row.get("recommended_action"),
    }
    return f"Assess operational risk for this product:\n```json\n{json.dumps(context, indent=2, default=str)}\n```"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_explanation(product_row: dict) -> str:
    """
    Generate a natural-language explanation of a promotion recommendation.

    Args:
        product_row: A dict containing the structured output from
                     promotion_engine.recommend() merged with any raw CSV
                     fields needed for context. Must include at minimum:
                     product_name, dark_store_id, recommended_action,
                     reasons, options.

    Returns:
        A 3-5 sentence explanation string suitable for display on the
        retailer dashboard.
    """
    user_msg = _build_explanation_prompt(product_row)
    return _call_llm(
        messages=[
            {"role": "system", "content": EXPLANATION_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
    )


def generate_risk_flag(product_row: dict) -> str | None:
    """
    Generate a dark-store-specific risk warning, or None if no risk.

    Follows core architectural rule: Analytics checks thresholds deterministically;
    LLM phrases the warning into clear natural language.

    Args:
        product_row: Product data dict.

    Returns:
        A 1-sentence risk warning string, or None if no operational risk detected.
    """
    days_to_expiry = product_row.get("days_to_expiry", 999)
    current_stock = product_row.get("current_stock", 0)
    min_stock = product_row.get("minimum_stock", 0)
    stockout_risk = product_row.get("stockout_risk_pct", 0)
    price_gap = product_row.get("competitor_price_gap_pct", 0)
    neg_rate = product_row.get("negative_review_rate", 0)
    current_disc = product_row.get("current_discount_pct", 0)
    store_id = product_row.get("dark_store_id", "Dark Store")
    prod_name = product_row.get("product_name", "Product")

    # 1. Deterministic Rule Trigger Check
    detected_risks = []
    if days_to_expiry <= 2 and current_stock > min_stock:
        detected_risks.append(f"Imminent Expiry Waste: only {days_to_expiry} days left before expiry with {current_stock} units exceeding minimum stock of {min_stock}")
    if stockout_risk > 60:
        detected_risks.append(f"Imminent Stockout Risk: stockout risk is at {stockout_risk}% with inventory critically depleted")
    if price_gap > 20 and current_disc == 0:
        detected_risks.append(f"Customer Churn Risk: competitor price gap is {price_gap}% with no active discount in place")
    if neg_rate > 0.35 and current_stock > 15:
        detected_risks.append(f"Quality Dead-Stock Risk: negative review rate is {neg_rate*100:.1f}% on {current_stock} units of existing stock")

    if not detected_risks:
        return None

    # 2. Translate detected operational risk into concise dashboard alert via LLM
    alert_prompt = f"Convert this operational risk into a direct, professional 1-sentence warning for the store manager at {store_id} for {prod_name}: {detected_risks[0]}"
    try:
        return _call_llm(
            messages=[
                {"role": "system", "content": "You are a concise retail operations assistant. Output ONLY a single professional alert sentence. No thinking, no markdown."},
                {"role": "user", "content": alert_prompt},
            ],
            temperature=0.1,
            max_tokens=100,
        )
    except Exception:
        # Fallback to direct structured string if API fails
        return f"Warning for {prod_name} at {store_id}: {detected_risks[0]}."


# ---------------------------------------------------------------------------
# Convenience: process a full engine output row end-to-end
# ---------------------------------------------------------------------------

def enrich_with_ai(engine_output: dict, raw_row: dict = None) -> dict:
    """
    Takes the structured output from promotion_engine.recommend() and
    enriches it with LLM-generated explanation and risk flag.

    Args:
        engine_output: The dict from promotion_engine.recommend()
        raw_row: Optional raw CSV row dict for extra context fields

    Returns:
        engine_output with two new keys added:
            'explanation' (str) and 'risk_warning' (str | None)
    """
    # Merge raw row context into engine output for richer prompts
    merged = {}
    if raw_row:
        merged.update(raw_row)
    merged.update(engine_output)  # engine output takes precedence

    merged["explanation"] = generate_explanation(merged)
    merged["risk_warning"] = generate_risk_flag(merged)
    return merged


# ---------------------------------------------------------------------------
# Sample test data (pulled from the output contract in the handoff doc)
# ---------------------------------------------------------------------------

SAMPLE_ROWS = [
    # Row 1: CLEARANCE — expiry critical, 0 days left
    {
        "product_id": "P0059",
        "product_name": "Nuts Medium",
        "dark_store_id": "BEN-DS4",
        "category": "Snacks",
        "recommended_action": "CLEARANCE",
        "discount_pct": 25,
        "objective_used": "Balanced",
        "reasons": ["expiry_urgency=Critical (0 days left of 1-day shelf life)"],
        "risk_flag": "EXPIRY_CRITICAL",
        "inventory_snapshot": {
            "stock_position_pct": 100.0,
            "understock": False,
            "overstock": True,
            "days_of_cover": 7.3,
            "expiry_urgency": "Critical",
            "stockout_urgency": "High",
            "overstock_urgency": "Critical",
            "inventory_alert_score": 100,
        },
        "options": [
            {
                "discount_pct": 25,
                "expected_units": 3.1,
                "expected_profit": 47.6,
                "inventory_reduction_pct": 12.4,
                "stockout_risk_pct": 15.6,
                "score": 47.63,
            },
            {
                "discount_pct": 35,
                "expected_units": 3.4,
                "expected_profit": 10.0,
                "inventory_reduction_pct": 13.6,
                "stockout_risk_pct": 16.1,
                "score": 10.04,
            },
            {
                "discount_pct": 45,
                "expected_units": 3.6,
                "expected_profit": -32.5,
                "inventory_reduction_pct": 14.4,
                "stockout_risk_pct": 16.6,
                "score": -32.52,
            },
        ],
        "chosen_option": {
            "discount_pct": 25,
            "expected_units": 3.1,
            "expected_profit": 47.6,
            "inventory_reduction_pct": 12.4,
            "stockout_risk_pct": 15.6,
            "score": 47.63,
        },
        # Raw CSV fields for risk assessment
        "current_stock": 25,
        "minimum_stock": 10,
        "maximum_stock": 25,
        "days_to_expiry": 0,
        "shelf_life_days": 1,
        "stock_turnover_days": 7,
        "stockout_risk_pct": 15.6,
        "demand_trend_pct": -5.0,
        "demand_status": "Flat",
        "competitor_price_gap_pct": 3.2,
        "competitor_discount_pct": 10,
        "current_discount_pct": 0,
        "negative_review_rate": 0.08,
        "product_rating": 4.2,
        "mrp": 250,
        "unit_price": 230,
        "sales_7d": 24,
        "sales_30d": 95,
    },
    # Row 2: REVIEW PRODUCT QUALITY — low rating, high negative reviews
    {
        "product_id": "P0173",
        "product_name": "Organic Honey 500g",
        "dark_store_id": "MUM-DS2",
        "category": "Condiments",
        "recommended_action": "REVIEW PRODUCT QUALITY",
        "discount_pct": 0,
        "objective_used": "Balanced",
        "reasons": [
            "product_rating=2.1 (below 3.0 threshold)",
            "negative_review_rate=0.52 (above 0.40 threshold)",
        ],
        "risk_flag": "QUALITY_ISSUE",
        "inventory_snapshot": {
            "stock_position_pct": 72.0,
            "understock": False,
            "overstock": False,
            "days_of_cover": 18.5,
            "expiry_urgency": "Low",
            "stockout_urgency": "Low",
            "overstock_urgency": "Low",
            "inventory_alert_score": 35,
        },
        "options": [],
        "chosen_option": {},
        "current_stock": 36,
        "minimum_stock": 10,
        "maximum_stock": 50,
        "days_to_expiry": 120,
        "shelf_life_days": 365,
        "stock_turnover_days": 18,
        "stockout_risk_pct": 5.0,
        "demand_trend_pct": -22.0,
        "demand_status": "Declining",
        "competitor_price_gap_pct": 8.5,
        "competitor_discount_pct": 5,
        "current_discount_pct": 0,
        "negative_review_rate": 0.52,
        "product_rating": 2.1,
        "mrp": 450,
        "unit_price": 420,
        "sales_7d": 14,
        "sales_30d": 62,
    },
    # Row 3: COMPETITIVE PRICE OFFER — big price gap to competitors
    {
        "product_id": "P0312",
        "product_name": "Basmati Rice 5kg",
        "dark_store_id": "DEL-DS7",
        "category": "Staples",
        "recommended_action": "COMPETITIVE PRICE OFFER",
        "discount_pct": 12,
        "objective_used": "Balanced",
        "reasons": [
            "competitor_price_gap_pct=22.3% (above 15% threshold)",
            "competitor_discount_pct=18% vs our 0%",
        ],
        "risk_flag": None,
        "inventory_snapshot": {
            "stock_position_pct": 55.0,
            "understock": False,
            "overstock": False,
            "days_of_cover": 12.0,
            "expiry_urgency": "Low",
            "stockout_urgency": "Low",
            "overstock_urgency": "Low",
            "inventory_alert_score": 20,
        },
        "options": [
            {
                "discount_pct": 10,
                "expected_units": 48.2,
                "expected_profit": 1250.0,
                "inventory_reduction_pct": 8.5,
                "stockout_risk_pct": 12.0,
                "score": 65.3,
            },
            {
                "discount_pct": 15,
                "expected_units": 55.1,
                "expected_profit": 980.0,
                "inventory_reduction_pct": 11.2,
                "stockout_risk_pct": 18.5,
                "score": 58.7,
            },
            {
                "discount_pct": 20,
                "expected_units": 60.8,
                "expected_profit": 620.0,
                "inventory_reduction_pct": 14.0,
                "stockout_risk_pct": 25.3,
                "score": 42.1,
            },
        ],
        "chosen_option": {
            "discount_pct": 10,
            "expected_units": 48.2,
            "expected_profit": 1250.0,
            "inventory_reduction_pct": 8.5,
            "stockout_risk_pct": 12.0,
            "score": 65.3,
        },
        "current_stock": 110,
        "minimum_stock": 30,
        "maximum_stock": 200,
        "days_to_expiry": 180,
        "shelf_life_days": 365,
        "stock_turnover_days": 12,
        "stockout_risk_pct": 12.0,
        "demand_trend_pct": 8.0,
        "demand_status": "Rising",
        "competitor_price_gap_pct": 22.3,
        "competitor_discount_pct": 18,
        "current_discount_pct": 0,
        "negative_review_rate": 0.05,
        "product_rating": 4.5,
        "mrp": 680,
        "unit_price": 650,
        "sales_7d": 64,
        "sales_30d": 245,
    },
    # Row 4: NO PROMOTION — stockout risk, can't afford to discount
    {
        "product_id": "P0088",
        "product_name": "Toned Milk 1L",
        "dark_store_id": "BEN-DS1",
        "category": "Dairy",
        "recommended_action": "NO PROMOTION",
        "discount_pct": 0,
        "objective_used": "Balanced",
        "reasons": [
            "stockout_urgency=Critical (0.8 days of cover)",
            "current_stock=4 vs minimum_stock=15",
        ],
        "risk_flag": "STOCKOUT_IMMINENT",
        "inventory_snapshot": {
            "stock_position_pct": 16.0,
            "understock": True,
            "overstock": False,
            "days_of_cover": 0.8,
            "expiry_urgency": "Medium",
            "stockout_urgency": "Critical",
            "overstock_urgency": "Low",
            "inventory_alert_score": 92,
        },
        "options": [],
        "chosen_option": {},
        "current_stock": 4,
        "minimum_stock": 15,
        "maximum_stock": 25,
        "days_to_expiry": 2,
        "shelf_life_days": 5,
        "stock_turnover_days": 1,
        "stockout_risk_pct": 85.0,
        "demand_trend_pct": 32.0,
        "demand_status": "Rising",
        "competitor_price_gap_pct": 2.1,
        "competitor_discount_pct": 0,
        "current_discount_pct": 0,
        "negative_review_rate": 0.03,
        "product_rating": 4.6,
        "mrp": 68,
        "unit_price": 62,
        "sales_7d": 35,
        "sales_30d": 150,
    },
    # Row 5: PROMOTE — rising demand, viral trend, healthy stock
    {
        "product_id": "P0201",
        "product_name": "Protein Bar Chocolate",
        "dark_store_id": "HYD-DS3",
        "category": "Health Foods",
        "recommended_action": "PROMOTE",
        "discount_pct": 15,
        "objective_used": "Sales",
        "reasons": [
            "demand_trend_pct=45% (above 15% threshold)",
            "trend_signal=viral",
            "stock healthy: days_of_cover=14.2, no expiry risk",
        ],
        "risk_flag": None,
        "inventory_snapshot": {
            "stock_position_pct": 60.0,
            "understock": False,
            "overstock": False,
            "days_of_cover": 14.2,
            "expiry_urgency": "Low",
            "stockout_urgency": "Low",
            "overstock_urgency": "Low",
            "inventory_alert_score": 10,
        },
        "options": [
            {
                "discount_pct": 10,
                "expected_units": 82.0,
                "expected_profit": 3200.0,
                "inventory_reduction_pct": 15.0,
                "stockout_risk_pct": 8.0,
                "score": 78.5,
            },
            {
                "discount_pct": 15,
                "expected_units": 95.3,
                "expected_profit": 2800.0,
                "inventory_reduction_pct": 18.5,
                "stockout_risk_pct": 14.0,
                "score": 82.1,
            },
            {
                "discount_pct": 20,
                "expected_units": 105.7,
                "expected_profit": 2100.0,
                "inventory_reduction_pct": 22.0,
                "stockout_risk_pct": 20.5,
                "score": 72.3,
            },
        ],
        "chosen_option": {
            "discount_pct": 15,
            "expected_units": 95.3,
            "expected_profit": 2800.0,
            "inventory_reduction_pct": 18.5,
            "stockout_risk_pct": 14.0,
            "score": 82.1,
        },
        "current_stock": 90,
        "minimum_stock": 20,
        "maximum_stock": 150,
        "days_to_expiry": 90,
        "shelf_life_days": 180,
        "stock_turnover_days": 5,
        "stockout_risk_pct": 8.0,
        "demand_trend_pct": 45.0,
        "demand_status": "Rising",
        "competitor_price_gap_pct": 5.0,
        "competitor_discount_pct": 12,
        "current_discount_pct": 0,
        "negative_review_rate": 0.04,
        "product_rating": 4.4,
        "mrp": 180,
        "unit_price": 160,
        "sales_7d": 45,
        "sales_30d": 160,
    },
]


# ---------------------------------------------------------------------------
# Test runner
# ---------------------------------------------------------------------------

def run_tests():
    """Run generate_explanation and generate_risk_flag on all sample rows."""
    print("=" * 70, flush=True)
    print("AI ENGINE — Testing on", len(SAMPLE_ROWS), "sample rows", flush=True)
    print(f"Primary: {NVIDIA_PRIMARY_MODEL} (NVIDIA NIM) | Fallback: {GROQ_MODEL} (Groq)", flush=True)
    print("=" * 70, flush=True)

    for i, row in enumerate(SAMPLE_ROWS, 1):
        print(f"\n{'─' * 70}", flush=True)
        print(f"ROW {i}: {row['product_name']} @ {row['dark_store_id']}", flush=True)
        print(f"Action: {row['recommended_action']}  |  Reasons: {row['reasons']}", flush=True)
        print(f"{'─' * 70}", flush=True)

        try:
            explanation = generate_explanation(row)
            print(f"\n📝 EXPLANATION:\n{explanation}", flush=True)
        except Exception as e:
            print(f"\n❌ EXPLANATION ERROR: {e}", flush=True)

        try:
            risk = generate_risk_flag(row)
            if risk:
                print(f"\n⚠️  RISK FLAG:\n{risk}", flush=True)
            else:
                print(f"\n✅ RISK FLAG: None (no operational risk detected)", flush=True)
        except Exception as e:
            print(f"\n❌ RISK FLAG ERROR: {e}", flush=True)

    print(f"\n{'=' * 70}", flush=True)
    print("All tests complete.", flush=True)
    print("=" * 70, flush=True)


if __name__ == "__main__":
    run_tests()
