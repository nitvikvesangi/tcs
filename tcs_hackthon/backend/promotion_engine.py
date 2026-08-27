def generate_promotion_options(product_row: dict) -> dict:
    """
    Determines the best promotion strategy and options.
    Extracts the options and recommendation from the dataset row.
    """
    options = product_row.get("options", [])
    recommendation = product_row.get("recommendation", {
        "action": product_row.get("recommended_action", "NO PROMOTION"),
        "discount_pct": product_row.get("discount_pct", 0),
        "objective": "BALANCE_INVENTORY"
    })
    
    return {
        "options": options,
        "recommendation": recommendation
    }
