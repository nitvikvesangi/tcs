import json
import os
from typing import List, Dict, Any

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "dataset.json")

def load_dataset() -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def query_products(filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Simulates Person 1's data layer querying.
    """
    data = load_dataset()
    if not filters:
        return data
        
    filtered_data = []
    for item in data:
        match = True
        if filters.get("city") and item.get("city") != filters["city"]:
            match = False
        if filters.get("dark_store_id") and item.get("dark_store_id") != filters["dark_store_id"]:
            match = False
        if filters.get("category") and item.get("category") != filters["category"]:
            match = False
        if filters.get("demand_status") and item.get("demand_status") != filters["demand_status"]:
            match = False
        if filters.get("search_query"):
            q = filters["search_query"].lower()
            if q not in item.get("product_name", "").lower() and q not in item.get("product_id", "").lower():
                match = False
                
        if match:
            filtered_data.append(item)
            
    return filtered_data
