"""
promo_recommender.py — simple rule-based promotion logic.

Takes product dicts (from data_loader.query_products) and decides:
- whether to promote
- how big a discount to suggest
- why (so you can explain it to judges)

No ML, just thresholds. Tune the numbers in CONFIG to taste.
"""

from data_loader import query_products

# ---------------------------------------------------------------------------
# Thresholds — tweak these during the hackathon if results look off
# ---------------------------------------------------------------------------
CONFIG = {
    "expiry_urgent_days": 7,       # <= this many days left = urgent
    "stockout_risk_high_pct": 15,  # >= this = too risky to discount
    "demand_falling_pct": 0,       # negative = demand is dropping
    "min_margin_for_discount": 10, # need at least this margin % to discount
}


def recommend_for_product(product):
    """
    Takes one product dict (matching query_products() output keys)
    and returns a dict with: action, discount_pct, reason.
    """
    stockout_risk = product["stockout_risk_pct"]
    days_left = product["days_to_expiry"]
    demand_trend = product["demand_trend_pct"]
    margin = product["gross_margin_before_promo"]

    # Rule 1: too risky to discount — protect remaining stock
    if stockout_risk >= CONFIG["stockout_risk_high_pct"]:
        return {
            "action": "NO PROMOTION",
            "discount_pct": 0,
            "reason": f"Stockout risk too high ({stockout_risk}%) — don't push more demand.",
        }

    # Rule 2: expiring soon — clear it out
    if days_left <= CONFIG["expiry_urgent_days"]:
        return {
            "action": "CLEARANCE",
            "discount_pct": 25,
            "reason": f"Only {days_left} days to expiry — move it fast.",
        }

    # Rule 3: demand falling and margin can absorb a discount — revive sales
    if demand_trend < CONFIG["demand_falling_pct"] and margin >= CONFIG["min_margin_for_discount"]:
        return {
            "action": "PROMOTE",
            "discount_pct": 15,
            "reason": f"Demand falling ({demand_trend}%) — margin ({margin}%) can absorb a discount.",
        }

    # Rule 4: default — leave it alone
    return {
        "action": "NO PROMOTION",
        "discount_pct": 0,
        "reason": "No urgent signal — product is fine as-is.",
    }


def recommend_batch(products):
    """Takes a list of product dicts, returns a list of
    {**product, 'action':..., 'discount_pct':..., 'reason':...}"""
    results = []
    for product in products:
        rec = recommend_for_product(product)
        results.append({**product, **rec})
    return results


if __name__ == "__main__":
    products = query_products(city="Hyderabad")
    recommendations = recommend_batch(products)

    print(f"\n{len(recommendations)} products checked for Hyderabad.\n")
    for r in recommendations[:5]:
        print(f"{r['product_name']:20s} -> {r['action']:15s} "
              f"discount={r['discount_pct']}%  | {r['reason']}")