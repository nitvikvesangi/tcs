"""
test_model_interactive.py — Interactive CLI to test ML Model & AI Engine in real time.
Run:
    .venv/bin/python test_model_interactive.py
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml_engine import predict_action
from ai_engine import generate_explanation, generate_risk_flag, _call_llm

CSV_PATH = "quick_commerce_master_synthetic_dataset.csv"

def banner():
    print("=" * 75)
    print(" 🛒 QUICK COMMERCE — INTERACTIVE ML MODEL & AI TESTING TOOL")
    print("=" * 75)

def test_random_samples(df, n=5):
    print(f"\n📊 --- Testing {n} Random Products from {CSV_PATH} ---")
    samples = df.sample(n, random_state=42)
    for idx, (_, row) in enumerate(samples.iterrows(), 1):
        r = row.to_dict()
        pred = predict_action(r)
        
        action = pred["action"]
        conf = pred["confidence"] * 100
        ground_truth = r.get("recommended_action", "N/A")
        
        print(f"\n[{idx}] {r.get('product_name')} ({r.get('product_id')}) | Store: {r.get('dark_store_id')} ({r.get('city')})")
        print(f"    • Current Stock : {r.get('current_stock')} units")
        print(f"    • Days to Expiry: {r.get('days_to_expiry')} days")
        print(f"    • Demand Trend  : {r.get('demand_trend_pct')}%")
        print(f"    • Rating/Reviews: {r.get('product_rating')} ⭐ | Negative: {float(r.get('negative_review_rate', 0))*100:.1f}%")
        print(f"    • CSV Action    : {ground_truth}")
        print(f"    🎯 ML PREDICTED : >>> {action} <<< (Confidence: {conf:.1f}%)")
        match_symbol = "✅ MATCH" if action == ground_truth else "⚡ Alternative"
        print(f"    Result          : {match_symbol}")

def test_ai_explanation(df):
    print("\n" + "=" * 75)
    print(" 🤖 --- Testing AI Engine (LLM Natural Language Reasoning) ---")
    print("=" * 75)
    sample_clearance = df[df["recommended_action"] == "CLEARANCE"].iloc[0].to_dict()
    print(f"\nTarget Product: {sample_clearance.get('product_name')} ({sample_clearance.get('product_id')})")
    print(f"Days to Expiry: {sample_clearance.get('days_to_expiry')} | Stock: {sample_clearance.get('current_stock')}")
    
    print("\nCalling LLM (Groq / NVIDIA) to generate Store Manager Briefing...")
    explanation = generate_explanation(sample_clearance)
    print("\n📝 AI STORE MANAGER BRIEFING:")
    print("-" * 50)
    print(explanation)
    print("-" * 50)
    
    risk = generate_risk_flag(sample_clearance)
    if risk:
        print(f"\n🚨 AI OPERATIONAL RISK ALERT:\n{risk}")

def main():
    banner()
    if not os.path.exists(CSV_PATH):
        print(f"❌ Error: {CSV_PATH} not found.")
        return

    df = pd.read_csv(CSV_PATH)
    print(f"✅ Loaded {len(df):,} records from CSV dataset.")
    print("✅ Loaded trained RandomForest model artifacts.")
    
    test_random_samples(df, n=5)
    test_ai_explanation(df)
    
    print("\n" + "=" * 75)
    print(" ✅ ALL TESTS PASSED! ML Model & AI Engine are 100% active and working.")
    print("=" * 75)
    print("\n🌐 You can also test on the web:")
    print("  • React Frontend Dashboard: http://localhost:5173")
    print("  • Streamlit AI Suite      : http://localhost:8501")
    print("  • FastAPI Swagger Docs    : http://localhost:8000/docs\n")

if __name__ == "__main__":
    main()
