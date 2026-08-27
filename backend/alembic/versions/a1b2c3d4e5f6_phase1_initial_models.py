"""Phase 1 — initial models: all 16 tables.

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-08-27 13:56:27

Tables created (in FK dependency order):
  retailers, users, dark_stores, products, inventory,
  customers, customer_events, orders, order_items,
  reviews, promotions, promotion_performance,
  weather, festivals, trends, competitor_prices
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------------
    # Enum types (PostgreSQL-specific; silently skipped on SQLite)
    # ---------------------------------------------------------------
    userrole = sa.Enum(
        "RETAILER_ADMIN", "STORE_MANAGER", "ANALYST", name="userrole"
    )
    storestatus = sa.Enum(
        "ACTIVE", "INACTIVE", "TEMPORARILY_CLOSED", name="storestatus"
    )
    customersegment = sa.Enum(
        "BUDGET_CONSCIOUS", "PREMIUM", "FREQUENT_BUYER",
        "OCCASIONAL_BUYER", "NEW_CUSTOMER", "HIGH_VALUE_CUSTOMER",
        name="customersegment",
    )
    customereventtype = sa.Enum(
        "VIEW", "SEARCH", "CART_ADD", "PURCHASE", name="customereventtype"
    )
    orderstatus = sa.Enum(
        "PLACED", "CONFIRMED", "DELIVERED", "CANCELLED", "RETURNED",
        name="orderstatus",
    )
    promotiontype = sa.Enum(
        "PERCENTAGE_DISCOUNT", "FIXED_DISCOUNT", "BUNDLE",
        "BUY_ONE_GET_ONE", "CLEARANCE", "NO_PROMOTION",
        name="promotiontype",
    )
    promotionobjective = sa.Enum(
        "MAXIMIZE_PROFIT", "MAXIMIZE_SALES", "CLEAR_INVENTORY",
        "REDUCE_EXPIRY_WASTE", "INCREASE_RETENTION",
        "INCREASE_AOV", "BALANCED",
        name="promotionobjective",
    )
    promotionstatus = sa.Enum(
        "RECOMMENDED", "APPROVED", "REJECTED", "EXPIRED",
        name="promotionstatus",
    )
    riskflag = sa.Enum(
        "NONE", "EXPIRY_CRITICAL", "STOCKOUT_RISK",
        "OVERSTOCK_RISK", "MARGIN_TOO_LOW", "NO_VALID_PROMOTION",
        name="riskflag",
    )
    weathercondition = sa.Enum(
        "SUNNY", "RAINY", "CLOUDY", "HOT", "COLD", "STORMY",
        name="weathercondition",
    )
    demandtrend = sa.Enum(
        "INCREASING", "STABLE", "DECLINING", name="demandtrend"
    )

    # ---------------------------------------------------------------
    # retailers
    # ---------------------------------------------------------------
    op.create_table(
        "retailers",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_retailers_email", "retailers", ["email"], unique=True)

    # ---------------------------------------------------------------
    # users
    # ---------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("role", userrole, nullable=False),
        sa.Column("retailer_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["retailer_id"], ["retailers.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_retailer_id", "users", ["retailer_id"])

    # ---------------------------------------------------------------
    # dark_stores
    # ---------------------------------------------------------------
    op.create_table(
        "dark_stores",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("retailer_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("address", sa.String(500), nullable=True),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("status", storestatus, nullable=False),
        sa.Column("opening_time", sa.String(5), nullable=True),
        sa.Column("closing_time", sa.String(5), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["retailer_id"], ["retailers.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dark_stores_code", "dark_stores", ["code"], unique=True)
    op.create_index("ix_dark_stores_city", "dark_stores", ["city"])
    op.create_index("ix_dark_stores_retailer_id", "dark_stores", ["retailer_id"])
    op.create_index("ix_dark_stores_retailer_city", "dark_stores", ["retailer_id", "city"])

    # ---------------------------------------------------------------
    # products
    # ---------------------------------------------------------------
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("sku", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("subcategory", sa.String(100), nullable=True),
        sa.Column("brand", sa.String(100), nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("mrp", sa.Numeric(10, 2), nullable=False),
        sa.Column("cost_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("shelf_life_days", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)
    op.create_index("ix_products_category", "products", ["category"])

    # ---------------------------------------------------------------
    # inventory
    # ---------------------------------------------------------------
    op.create_table(
        "inventory",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("dark_store_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity_available", sa.Integer(), nullable=False),
        sa.Column("quantity_reserved", sa.Integer(), nullable=False),
        sa.Column("reorder_point", sa.Integer(), nullable=False),
        sa.Column("max_stock", sa.Integer(), nullable=True),
        sa.Column("batch_number", sa.String(100), nullable=True),
        sa.Column("manufactured_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("last_restocked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["dark_store_id"], ["dark_stores.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_inventory_store_product", "inventory", ["dark_store_id", "product_id"])
    op.create_index("ix_inventory_expiry_date", "inventory", ["expiry_date"])

    # ---------------------------------------------------------------
    # customers
    # ---------------------------------------------------------------
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("retailer_id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.String(100), nullable=True),
        sa.Column("segment", customersegment, nullable=False),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["retailer_id"], ["retailers.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_customers_retailer_id", "customers", ["retailer_id"])
    op.create_index("ix_customers_external_id", "customers", ["external_id"])

    # ---------------------------------------------------------------
    # orders
    # ---------------------------------------------------------------
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("dark_store_id", sa.Integer(), nullable=False),
        sa.Column("status", orderstatus, nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "placed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["customer_id"], ["customers.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["dark_store_id"], ["dark_stores.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_orders_customer_id", "orders", ["customer_id"])
    op.create_index("ix_orders_dark_store_id", "orders", ["dark_store_id"])
    op.create_index("ix_orders_store_placed", "orders", ["dark_store_id", "placed_at"])

    # ---------------------------------------------------------------
    # order_items
    # ---------------------------------------------------------------
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("discount_pct", sa.Numeric(5, 2), nullable=False),
        sa.Column("total_price", sa.Numeric(12, 2), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])
    op.create_index("ix_order_items_product", "order_items", ["product_id"])

    # ---------------------------------------------------------------
    # customer_events
    # ---------------------------------------------------------------
    op.create_table(
        "customer_events",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("dark_store_id", sa.Integer(), nullable=False),
        sa.Column("event_type", customereventtype, nullable=False),
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.Column("search_query", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"], ["customers.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["dark_store_id"], ["dark_stores.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ce_customer_event_type", "customer_events", ["customer_id", "event_type"])
    op.create_index("ix_ce_product_event_type", "customer_events", ["product_id", "event_type"])
    op.create_index("ix_ce_store_created", "customer_events", ["dark_store_id", "created_at"])
    op.create_index("ix_ce_customer_product", "customer_events", ["customer_id", "product_id"])

    # ---------------------------------------------------------------
    # reviews
    # ---------------------------------------------------------------
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("dark_store_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("sentiment_score", sa.Numeric(4, 3), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"], ["customers.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["dark_store_id"], ["dark_stores.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reviews_product_id", "reviews", ["product_id"])
    op.create_index("ix_reviews_store_id", "reviews", ["dark_store_id"])

    # ---------------------------------------------------------------
    # promotions
    # ---------------------------------------------------------------
    op.create_table(
        "promotions",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("dark_store_id", sa.Integer(), nullable=False),
        sa.Column("promotion_type", promotiontype, nullable=False),
        sa.Column("objective", promotionobjective, nullable=False),
        sa.Column("status", promotionstatus, nullable=False),
        sa.Column("discount_pct", sa.Numeric(5, 2), nullable=False),
        sa.Column("risk_flag", riskflag, nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("approved_by_id", sa.Integer(), nullable=True),
        sa.Column("recommendation_data", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["dark_store_id"], ["dark_stores.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["approved_by_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_promotions_store_product", "promotions", ["dark_store_id", "product_id"])
    op.create_index("ix_promotions_status", "promotions", ["status"])
    op.create_index("ix_promotions_created", "promotions", ["created_at"])

    # ---------------------------------------------------------------
    # promotion_performance
    # ---------------------------------------------------------------
    op.create_table(
        "promotion_performance",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("promotion_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("units_sold", sa.Integer(), nullable=False),
        sa.Column("revenue", sa.Numeric(12, 2), nullable=False),
        sa.Column("profit", sa.Numeric(12, 2), nullable=False),
        sa.Column("inventory_reduction_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("stockout_occurred", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["promotion_id"], ["promotions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pp_promotion_id", "promotion_performance", ["promotion_id"])

    # ---------------------------------------------------------------
    # weather
    # ---------------------------------------------------------------
    op.create_table(
        "weather",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("dark_store_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("condition", weathercondition, nullable=False),
        sa.Column("temperature_c", sa.Numeric(5, 2), nullable=True),
        sa.Column("humidity_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("rainfall_mm", sa.Numeric(6, 2), nullable=True),
        sa.ForeignKeyConstraint(
            ["dark_store_id"], ["dark_stores.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dark_store_id", "date", name="uq_weather_store_date"),
    )
    op.create_index("ix_weather_store_date", "weather", ["dark_store_id", "date"])

    # ---------------------------------------------------------------
    # festivals
    # ---------------------------------------------------------------
    op.create_table(
        "festivals",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("demand_multiplier", sa.Numeric(4, 2), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_festivals_city_date", "festivals", ["city", "date"])
    op.create_index("ix_festivals_city", "festivals", ["city"])

    # ---------------------------------------------------------------
    # trends
    # ---------------------------------------------------------------
    op.create_table(
        "trends",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("trend_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("demand_trend", demandtrend, nullable=False),
        sa.Column("sales_velocity", sa.Numeric(10, 2), nullable=True),
        sa.Column("search_volume", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "date", name="uq_trend_product_date"),
    )
    op.create_index("ix_trends_product_date", "trends", ["product_id", "date"])

    # ---------------------------------------------------------------
    # competitor_prices
    # ---------------------------------------------------------------
    op.create_table(
        "competitor_prices",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("dark_store_id", sa.Integer(), nullable=False),
        sa.Column("competitor_name", sa.String(255), nullable=False),
        sa.Column("competitor_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("our_price", sa.Numeric(10, 2), nullable=True),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["dark_store_id"], ["dark_stores.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_competitor_prices_product_store",
        "competitor_prices",
        ["product_id", "dark_store_id"],
    )
    op.create_index(
        "ix_competitor_prices_recorded_at",
        "competitor_prices",
        ["recorded_at"],
    )


def downgrade() -> None:
    op.drop_table("competitor_prices")
    op.drop_table("trends")
    op.drop_table("festivals")
    op.drop_table("weather")
    op.drop_table("promotion_performance")
    op.drop_table("promotions")
    op.drop_table("reviews")
    op.drop_table("customer_events")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("customers")
    op.drop_table("inventory")
    op.drop_table("products")
    op.drop_table("dark_stores")
    op.drop_table("users")
    op.drop_table("retailers")
