"""
train_model.py — Train RandomForest on the CSV dataset and save artifacts.

Run once:
    python train_model.py

Saves:
    models/promotion_model.pkl
    models/encoders.pkl
"""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

CSV_PATH = "quick_commerce_master_synthetic_dataset.csv"
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)

FEATURE_COLS = [
    'days_to_expiry', 'shelf_life_days', 'current_stock', 'minimum_stock',
    'maximum_stock', 'stock_turnover_days', 'stockout_risk_pct', 'stockout_flag',
    'demand_trend_pct', 'demand_status', 'sales_7d', 'sales_30d',
    'historical_demand_30d', 'competitor_price_gap_pct', 'competitor_discount_pct',
    'product_rating', 'negative_review_rate', 'review_count', 'trend_signal',
    'product_popularity_score', 'is_weekend', 'festival_flag', 'local_event_flag',
    'gross_margin_before_promo', 'current_discount_pct',
]
TARGET_COL = 'recommended_action'
CATEGORICAL_COLS = ['demand_status', 'trend_signal']

print(f"Loading {CSV_PATH}...")
df = pd.read_csv(CSV_PATH)
print(f"Rows: {len(df)}")

# Check which feature cols exist
available = [c for c in FEATURE_COLS if c in df.columns]
missing = [c for c in FEATURE_COLS if c not in df.columns]
if missing:
    print(f"Missing columns (will use defaults): {missing}")
    for col in missing:
        df[col] = 0

# Verify target
if TARGET_COL not in df.columns:
    raise RuntimeError(f"Target column '{TARGET_COL}' not found in CSV. Columns: {list(df.columns)[:20]}")

print(f"Target distribution:\n{df[TARGET_COL].value_counts()}")

# Encode categoricals
encoders = {}
for col in CATEGORICAL_COLS:
    le = LabelEncoder()
    df[col] = df[col].fillna('Unknown').astype(str)
    le.fit(df[col].tolist() + ['Unknown'])
    df[col] = le.transform(df[col])
    encoders[col] = le

# Encode boolean
df['is_weekend'] = df['is_weekend'].astype(int)

# Encode target
target_le = LabelEncoder()
y = target_le.fit_transform(df[TARGET_COL].fillna('NO PROMOTION').astype(str))
encoders['__target__'] = target_le

# Feature matrix
X = df[FEATURE_COLS].fillna(0)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print(f"Train: {len(X_train)}, Test: {len(X_test)}")

# Train
print("Training RandomForest...")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=5,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1,
)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=target_le.classes_))

# Save
model_path = os.path.join(MODEL_DIR, "promotion_model.pkl")
encoders_path = os.path.join(MODEL_DIR, "encoders.pkl")
joblib.dump(model, model_path)
joblib.dump(encoders, encoders_path)
print(f"\n✅ Saved model → {model_path}")
print(f"✅ Saved encoders → {encoders_path}")
