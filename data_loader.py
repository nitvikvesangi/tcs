"""
data_loader.py — Data Layer — Neon PostgreSQL version

Loads CSV once (only if the DB table doesn't already exist) and
exposes query_products() as the one function everyone else calls.
"""

import os
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv()

CSV_PATH = "quick_commerce_master_synthetic_dataset.csv"
TABLE_NAME = "products_dataset"
DATABASE_URL = os.getenv("DATABASE_URL")

COLUMN_MAP = {
    "product_id": "product_id",
    "product_name": "product_name",
    "category": "category",
    "recommended_action": "recommended_action",
    "mrp": "mrp",
    "unit_cost": "unit_cost",
    "current_selling_price": "current_selling_price",
    "current_discount_pct": "current_discount_pct",
    "gross_margin_before_promo": "gross_margin_before_promo",
    "competitor_price": "competitor_price",
    "competitor_price_gap_pct": "competitor_price_gap_pct",
    "current_stock": "current_stock",
    "minimum_stock": "minimum_stock",
    "maximum_stock": "maximum_stock",
    "days_to_expiry": "days_to_expiry",
    "expiry_date": "expiry_date",
    "average_daily_sales": "average_daily_sales",
    "predicted_daily_demand": "predicted_daily_demand",
    "stockout_risk_pct": "stockout_risk_pct",
    "views_recent": "views_recent",
    "searches_recent": "searches_recent",
    "cart_adds_recent": "add_to_cart_count_7d",
    "purchases_recent": "purchase_count_7d",
    "repeat_purchase_rate": "repeat_purchase_rate",
    "average_rating": "product_rating",
    "negative_review_pct": "negative_review_rate",
    "city": "city",
    "dark_store_id": "dark_store_id",
    "weather_condition": "weather_condition",
    "time_of_day": "time_of_day",
    "is_weekend": "is_weekend",
    "festival_name": "festival_name",
    "festival_flag": "festival_flag",
    "local_event_flag": "local_event_flag",
    "trend_signal": "trend_signal",
    "demand_status": "demand_status",
    "demand_trend_pct": "demand_trend_pct",
}


def _load_dataframe(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Could not find CSV at '{csv_path}'.")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from {csv_path}")
    return df


def _add_computed_columns(df):
    df["current_selling_price"] = df["unit_price"]
    df["competitor_price"] = df[["competitor_1_price", "competitor_2_price"]].mean(axis=1)
    df["views_recent"] = df[["product_views_7d", "product_views_30d"]].mean(axis=1)
    df["average_daily_sales"] = (df["sales_7d"] / 7).round(2)
    df["predicted_daily_demand"] = (df["historical_demand_30d"] / 30).round(2)

    today = pd.Timestamp(datetime.now().date())
    df["expiry_date"] = (
        today + pd.to_timedelta(df["days_to_expiry"], unit="D")
    ).dt.strftime("%Y-%m-%d")

    df["repeat_purchase_rate"] = df["repeat_purchase_flag"]
    df["searches_recent"] = None
    df["festival_name"] = df["festival"]
    return df


def _get_engine():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL not found. Create a .env file with:\n"
            "DATABASE_URL=postgresql://<user>:<password>@<host>/<dbname>?sslmode=require"
        )
    return create_engine(DATABASE_URL)


def _ensure_table(engine, table_name, csv_path):
    """Upload CSV to Postgres only if the table does not already exist."""
    inspector = inspect(engine)
    if inspector.has_table(table_name):
        print(f"Table '{table_name}' already exists — skipping upload.")
        return
    print(f"Table '{table_name}' not found — uploading from CSV (one-time)...")
    df = _load_dataframe(csv_path)
    df = _add_computed_columns(df)
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"Uploaded {len(df)} rows to Postgres table '{table_name}'.")


# ---------------------------------------------------------------------------
# Initialise once on import
# ---------------------------------------------------------------------------
_ENGINE = _get_engine()
_ensure_table(_ENGINE, TABLE_NAME, CSV_PATH)


# ---------------------------------------------------------------------------
# Query function
# ---------------------------------------------------------------------------

def query_products(city=None, dark_store_id=None, category=None):
    """
    Query the products table with optional filters (None = no filter).
    Returns a list of dicts matching COLUMN_MAP keys.
    """
    select_cols = ", ".join(f'"{col}"' for col in COLUMN_MAP.values())
    query = f'SELECT {select_cols} FROM {TABLE_NAME} WHERE 1=1'
    params = {}

    if city is not None:
        query += " AND city = :city"
        params["city"] = city
    if dark_store_id is not None:
        query += ' AND "dark_store_id" = :dark_store_id'
        params["dark_store_id"] = dark_store_id
    if category is not None:
        query += " AND category = :category"
        params["category"] = category

    try:
        with _ENGINE.connect() as conn:
            rows = conn.execute(text(query), params).fetchall()
    except Exception as e:
        print(f"Postgres error while querying: {e}")
        return []

    if not rows:
        print("No results found for the given filters.")
        return []

    output_keys = list(COLUMN_MAP.keys())
    results = [dict(zip(output_keys, row)) for row in rows]
    return results


def get_products(city=None, dark_store=None):
    """Alias matching the team spec's exact function name/signature."""
    return query_products(city=city, dark_store_id=dark_store)


# ---------------------------------------------------------------------------
# Order placement
# ---------------------------------------------------------------------------

def place_order(product_id, dark_store_id, quantity):
    """
    Reduces current_stock for one product at one dark store by `quantity`.
    Returns success/failure dict.
    """
    try:
        with _ENGINE.connect() as conn:
            row = conn.execute(
                text(
                    f'SELECT current_stock FROM {TABLE_NAME} '
                    f'WHERE product_id = :pid AND dark_store_id = :store'
                ),
                {"pid": product_id, "store": dark_store_id},
            ).fetchone()

            if row is None:
                return {
                    "success": False,
                    "error": f"No product '{product_id}' found at dark store '{dark_store_id}'.",
                }

            current_stock = row[0]

            if quantity <= 0:
                return {"success": False, "error": "Quantity must be positive."}

            if quantity > current_stock:
                return {
                    "success": False,
                    "error": f"Not enough stock. Requested {quantity}, only {current_stock} available.",
                }

            new_stock = current_stock - quantity
            conn.execute(
                text(
                    f'UPDATE {TABLE_NAME} SET current_stock = :new_stock '
                    f'WHERE product_id = :pid AND dark_store_id = :store'
                ),
                {"new_stock": new_stock, "pid": product_id, "store": dark_store_id},
            )
            conn.commit()

        return {
            "success": True,
            "product_id": product_id,
            "dark_store_id": dark_store_id,
            "quantity_ordered": quantity,
            "new_stock": new_stock,
        }

    except Exception as e:
        return {"success": False, "error": f"Postgres error: {e}"}


if __name__ == "__main__":
    print("\n--- Test: query_products(city='Hyderabad') ---")
    results = query_products(city="Hyderabad")
    print(f"Found {len(results)} rows.")
    if results:
        for k, v in list(results[0].items())[:5]:
            print(f"  {k}: {v}")