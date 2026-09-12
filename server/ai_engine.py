def generate_explanation(product_row: dict) -> list:
    """
    Returns AI generated reasons for the promotion logic.
    """
    reasons = product_row.get("reasons")
    if reasons:
        return reasons
    
    # Fallback to explanation string
    explanation = product_row.get("explanation")
    if explanation:
        return [explanation]
    return ["AI model generated this recommendation based on current metrics."]

def generate_risk_flag(product_row: dict) -> str:
    """
    Returns the AI generated risk flag.
    """
    return product_row.get("risk_flag", "")
