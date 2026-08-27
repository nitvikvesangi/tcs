def calculate_inventory_alert(product_row: dict) -> dict:
    """
    Calculates inventory-related signals using available data.
    Since we are simulating the backend logic for the hackathon,
    we extract the pre-calculated inventory_snapshot from the dataset.
    If it were missing, we would compute it here based on current_stock, days_to_expiry, etc.
    """
    if "inventory_snapshot" in product_row:
        return product_row["inventory_snapshot"]
    
    # Fallback simulation logic if raw data didn't have it
    stock = product_row.get("current_stock", 0)
    expiry = product_row.get("days_to_expiry", 999)
    
    return {
        "stockout_urgency": "HIGH" if stock < 20 else "LOW",
        "overstock_urgency": "HIGH" if stock > 200 else "LOW",
        "expiry_urgency": "CRITICAL" if expiry < 7 else "LOW",
        "inventory_alert_score": 50
    }
