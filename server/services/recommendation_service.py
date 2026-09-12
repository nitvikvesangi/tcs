from data_loader import query_products
from inventory_engine import calculate_inventory_alert
from promotion_engine import generate_promotion_options
from ai_engine import generate_explanation, generate_risk_flag
from schemas.recommendation import RecommendationResponse

def get_recommendations(filters: dict = None) -> list[RecommendationResponse]:
    rows = query_products(filters)
    responses = []
    
    for row in rows:
        inv_snapshot = calculate_inventory_alert(row)
        promo_data = generate_promotion_options(row)
        reasons = generate_explanation(row)
        risk_flag = generate_risk_flag(row)
        
        # Build the structured Pydantic response
        try:
            resp = RecommendationResponse(
                product_id=row["product_id"],
                dark_store_id=row["dark_store_id"],
                recommendation=promo_data["recommendation"],
                reasons=reasons,
                risk_flag=risk_flag,
                options=promo_data["options"],
                inventory_snapshot=inv_snapshot,
                
                # Hyperlocal context
                product_name=row["product_name"],
                category=row["category"],
                city=row["city"],
                current_stock=row.get("current_stock", 0),
                days_to_expiry=row.get("days_to_expiry", 999),
                demand_status=row.get("demand_status", "Stable"),
                demand_trend_pct=row.get("demand_trend_pct", 0.0),
                trend_signal=row.get("trend_signal"),
                weather_condition=row.get("weather_condition"),
                time_of_day=row.get("time_of_day"),
                is_weekend=row.get("is_weekend"),
                gross_margin_before_promo=row.get("gross_margin_before_promo"),
                competitor_price_gap_pct=row.get("competitor_price_gap_pct"),
                stockout_risk_pct=row.get("stockout_risk_pct", 0.0)
            )
            responses.append(resp)
        except Exception as e:
            # In a real app we'd log the error and skip or handle missing fields
            print(f"Skipping row due to validation error: {e}")
            continue
            
    return responses
