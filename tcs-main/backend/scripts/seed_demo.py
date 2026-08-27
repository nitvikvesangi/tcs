"""
Demo data seed script — deterministic (seeded random) for reproducible results.

Usage:
    python scripts/seed_demo.py
    DATABASE_URL=sqlite:///./demo.db python scripts/seed_demo.py

Creates:
  - 2 Retailers, 5 DarkStores across 3 cities
  - 12 Products (deliberately varied scenarios)
  - Inventory with interesting cases (overstock, understock, expiry, etc.)
  - 60 days of Orders + OrderItems
  - CustomerEvents (view/search/cart_add/purchase)
  - Weather records (last 7 days)
  - Festivals (upcoming)
  - Trends (last 14 days)
  - CompetitorPrices
  - Reviews

Idempotent: can be run multiple times safely (clears existing data first).
"""

import sys
import os
import datetime
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Allow DATABASE_URL override so seed works without Postgres
_override_url = os.environ.get("DATABASE_URL")
if _override_url:
    os.environ.setdefault("DATABASE_URL", _override_url)
    # If SQLite override: patch the app engine before any imports use it
    if "sqlite" in _override_url:
        os.environ["DATABASE_URL"] = _override_url

from sqlalchemy import text
from app.core.database import SessionLocal, engine, Base
from app.models import (
    Retailer, User, DarkStore, Product, Inventory, Customer,
    CustomerEvent, Order, OrderItem, Review, Promotion,
    PromotionPerformance, Weather, Festival, Trend, CompetitorPrice,
)
from app.core.security import hash_password
from app.utils.enums import (
    CustomerEventType, CustomerSegment, DemandTrend, OrderStatus,
    PromotionObjective, PromotionStatus, PromotionType, RiskFlag,
    StoreStatus, UserRole, WeatherCondition,
)

rng = random.Random(42)  # deterministic

# ---------------------------------------------------------------------------
# Create tables
# ---------------------------------------------------------------------------

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created/verified")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def days_ago(n):
    return datetime.date.today() - datetime.timedelta(days=n)

def rand_date(start_days_ago, end_days_ago):
    d = rng.randint(end_days_ago, start_days_ago)
    return days_ago(d)


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------

def seed():
    db = SessionLocal()
    try:
        # ---- Clear existing data (FK-safe order) ----------------------------
        print("🗑  Clearing existing demo data...")
        db.execute(text("DELETE FROM promotion_performance"))
        db.execute(text("DELETE FROM promotions"))
        db.execute(text("DELETE FROM reviews"))
        db.execute(text("DELETE FROM customer_events"))
        db.execute(text("DELETE FROM order_items"))
        db.execute(text("DELETE FROM orders"))
        db.execute(text("DELETE FROM competitor_prices"))
        db.execute(text("DELETE FROM trends"))
        db.execute(text("DELETE FROM festivals"))
        db.execute(text("DELETE FROM weather"))
        db.execute(text("DELETE FROM inventory"))
        db.execute(text("DELETE FROM customers"))
        db.execute(text("DELETE FROM dark_stores"))
        db.execute(text("DELETE FROM users"))
        db.execute(text("DELETE FROM products"))
        db.execute(text("DELETE FROM retailers"))
        db.commit()

        # ---- Retailers & Users ---------------------------------------------
        print("👤 Creating retailers and users...")
        r1 = Retailer(name="FreshMart India", email="admin@freshmart.in", city="Delhi", phone="+91-9876543210")
        r2 = Retailer(name="QuickBasket", email="admin@quickbasket.in", city="Bangalore", phone="+91-9876543211")
        db.add_all([r1, r2])
        db.flush()

        u1 = User(email="admin@freshmart.in", password_hash=hash_password("Demo@1234"),
                  full_name="Priya Sharma", role=UserRole.RETAILER_ADMIN, retailer_id=r1.id, is_active=True)
        u2 = User(email="admin@quickbasket.in", password_hash=hash_password("Demo@1234"),
                  full_name="Rahul Gupta", role=UserRole.RETAILER_ADMIN, retailer_id=r2.id, is_active=True)
        db.add_all([u1, u2])
        db.flush()

        # ---- Dark Stores ----------------------------------------------------
        print("🏪 Creating dark stores...")
        stores_data = [
            (r1.id, "FreshMart Delhi-1", "DEL-DS1", "Delhi"),
            (r1.id, "FreshMart Delhi-2", "DEL-DS2", "Delhi"),
            (r1.id, "FreshMart Bangalore", "BLR-DS1", "Bangalore"),
            (r2.id, "QuickBasket Mumbai", "MUM-DS1", "Mumbai"),
            (r2.id, "QuickBasket Hyderabad", "HYD-DS1", "Hyderabad"),
        ]
        stores = []
        for retailer_id, name, code, city in stores_data:
            s = DarkStore(retailer_id=retailer_id, name=name, code=code, city=city,
                          status=StoreStatus.ACTIVE, opening_time="06:00", closing_time="23:00",
                          latitude=rng.uniform(12.9, 28.7), longitude=rng.uniform(77.0, 80.0))
            db.add(s)
            stores.append(s)
        db.flush()

        # ---- Products -------------------------------------------------------
        print("📦 Creating products...")
        products_data = [
            # SKU, Name, Category, Brand, Unit, MRP, Cost, ShelfLife, Description
            ("P0001", "Amul Milk 500ml", "Dairy", "Amul", "500ml", 30, 20, 2, "Fresh pasteurized milk"),
            ("P0002", "Brown Bread Loaf", "Bakery", "Britannia", "400g", 45, 28, 3, "Whole wheat brown bread"),
            ("P0003", "Basmati Rice 5kg", "Grains", "India Gate", "5kg", 450, 310, 365, "Premium long-grain basmati"),
            ("P0004", "Lays Chips Classic", "Snacks", "PepsiCo", "90g", 30, 18, 90, "Salted potato chips"),
            ("P0005", "Coca-Cola 1L", "Beverages", "Coca-Cola", "1L", 60, 38, 180, "Chilled soft drink"),
            ("P0006", "Maggi Noodles 4pk", "Instant Food", "Nestle", "280g", 56, 38, 180, "2-minute instant noodles"),
            ("P0007", "Organic Spinach 200g", "Vegetables", "FreshFarm", "200g", 35, 20, 3, "Fresh organic spinach"),
            ("P0008", "Dettol Handwash 200ml", "Hygiene", "Reckitt", "200ml", 99, 62, 730, "Antibacterial liquid soap"),
            ("P0009", "Greek Yogurt 400g", "Dairy", "Epigamia", "400g", 120, 75, 7, "High-protein Greek yogurt"),
            ("P0010", "Almonds 500g", "Dry Fruits", "Happilo", "500g", 499, 340, 365, "Premium California almonds"),
            ("P0059", "Full Cream Milk 1L", "Dairy", "Mother Dairy", "1L", 62, 44, 1, "Fresh full cream milk"),  # 1-day shelf life
            ("P0011", "Paneer 200g", "Dairy", "Amul", "200g", 80, 55, 5, "Fresh cottage cheese"),
        ]
        products = []
        for sku, name, cat, brand, unit, mrp, cost, shelf, desc in products_data:
            p = Product(sku=sku, name=name, category=cat, brand=brand, unit=unit,
                        mrp=mrp, cost_price=cost, shelf_life_days=shelf, description=desc, is_active=True)
            db.add(p)
            products.append(p)
        db.flush()

        # ---- Inventory (interesting scenarios) ------------------------------
        print("📊 Creating inventory with interesting scenarios...")
        today = datetime.date.today()
        inv_data = [
            # (store_idx, product_idx, qty_avail, qty_reserved, reorder_pt, max_stock, batch, expiry_offset_days)
            # Store DEL-DS1
            (0, 0, 5, 0, 20, 100, "BATCH-A", 2),       # P0001 Milk — UNDERSTOCK + EXPIRY WARNING
            (0, 1, 8, 0, 15, 80, "BATCH-B", 3),         # P0002 Bread — UNDERSTOCK + EXPIRY
            (0, 2, 500, 0, 20, 100, "BATCH-C", None),   # P0003 Rice — OVERSTOCK (500 vs max 100)
            (0, 3, 25, 5, 10, 50, "BATCH-D", None),     # P0004 Chips — normal
            (0, 4, 0, 0, 10, 60, "BATCH-E", None),      # P0005 Coke — STOCKOUT
            (0, 5, 200, 0, 15, 50, "BATCH-F", None),    # P0006 Maggi — OVERSTOCK
            (0, 6, 3, 0, 10, 40, "BATCH-G", 1),         # P0007 Spinach — UNDERSTOCK + CRITICAL EXPIRY
            (0, 7, 45, 5, 10, 80, "BATCH-H", None),     # P0008 Dettol — normal
            (0, 8, 20, 2, 8, 60, "BATCH-I", 6),         # P0009 Yogurt — expiry warning
            (0, 9, 30, 0, 5, 40, "BATCH-J", None),      # P0010 Almonds — normal
            (0, 10, 50, 0, 5, 30, "BATCH-K", 0),        # P0059 Milk 1L — CRITICAL EXPIRY
            (0, 11, 12, 2, 8, 40, "BATCH-L", 4),        # P0011 Paneer — expiry soon
            # Store DEL-DS2
            (1, 0, 80, 5, 20, 100, "BATCH-M", 2),
            (1, 2, 45, 0, 20, 100, "BATCH-N", None),
            (1, 5, 18, 0, 15, 50, "BATCH-O", None),
            (1, 10, 8, 0, 5, 30, "BATCH-P", 1),         # Expiry
            # Store BLR-DS1
            (2, 0, 60, 10, 20, 100, "BATCH-Q", 2),
            (2, 3, 15, 0, 10, 50, "BATCH-R", None),
            (2, 5, 35, 0, 15, 50, "BATCH-S", None),
            (2, 9, 12, 0, 5, 40, "BATCH-T", None),
            # Store MUM-DS1
            (3, 1, 25, 0, 15, 80, "BATCH-U", 2),
            (3, 4, 40, 5, 10, 60, "BATCH-V", None),
            (3, 7, 30, 0, 10, 80, "BATCH-W", None),
            # Store HYD-DS1
            (4, 2, 90, 0, 20, 100, "BATCH-X", None),
            (4, 5, 60, 0, 15, 50, "BATCH-Y", None),
        ]
        inventory_records = []
        for store_idx, prod_idx, qty, reserved, reorder, max_st, batch, expiry_offset in inv_data:
            expiry = (today + datetime.timedelta(days=expiry_offset)) if expiry_offset is not None else None
            inv = Inventory(
                dark_store_id=stores[store_idx].id,
                product_id=products[prod_idx].id,
                quantity_available=qty,
                quantity_reserved=reserved,
                reorder_point=reorder,
                max_stock=max_st,
                batch_number=batch,
                expiry_date=expiry,
                last_restocked_at=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=rng.randint(1,10)),
            )
            db.add(inv)
            inventory_records.append(inv)
        db.flush()

        # ---- Customers ------------------------------------------------------
        print("👥 Creating customers...")
        customers = []
        segments = list(CustomerSegment)
        cities = ["Delhi", "Bangalore", "Mumbai", "Hyderabad", "Chennai"]
        for i in range(50):
            c = Customer(
                retailer_id=r1.id if i < 30 else r2.id,
                external_id=f"EXT-{i+1:04d}",
                segment=segments[i % len(segments)],
                city=rng.choice(cities),
                is_active=1,
            )
            db.add(c)
            customers.append(c)
        db.flush()

        # ---- Orders + OrderItems + CustomerEvents ---------------------------
        print("🛒 Creating orders and events (60 days)...")
        for day_offset in range(60, 0, -1):
            order_date = today - datetime.timedelta(days=day_offset)
            order_dt = datetime.datetime.combine(order_date, datetime.time(rng.randint(8, 22), rng.randint(0, 59)))
            order_dt = order_dt.replace(tzinfo=datetime.timezone.utc)

            num_orders = rng.randint(2, 6)
            for _ in range(num_orders):
                customer = rng.choice(customers)
                store = rng.choice(stores[:3])  # DEL-DS1, DEL-DS2, BLR-DS1 most active

                order = Order(
                    customer_id=customer.id,
                    dark_store_id=store.id,
                    status=OrderStatus.DELIVERED,
                    total_amount=0,
                    discount_amount=0,
                    placed_at=order_dt,
                    delivered_at=order_dt + datetime.timedelta(minutes=rng.randint(20, 45)),
                )
                db.add(order)
                db.flush()

                order_total = 0.0
                num_items = rng.randint(1, 4)
                used_products = rng.sample(range(len(products)), min(num_items, len(products)))
                for prod_idx in used_products:
                    prod = products[prod_idx]
                    qty = rng.randint(1, 3)
                    unit_price = float(prod.mrp)
                    total_price = qty * unit_price
                    order_total += total_price
                    oi = OrderItem(
                        order_id=order.id,
                        product_id=prod.id,
                        quantity=qty,
                        unit_price=unit_price,
                        discount_pct=0,
                        total_price=total_price,
                    )
                    db.add(oi)

                    # CustomerEvent: PURCHASE
                    db.add(CustomerEvent(
                        customer_id=customer.id,
                        product_id=prod.id,
                        dark_store_id=store.id,
                        event_type=CustomerEventType.PURCHASE,
                        session_id=f"S-{day_offset}-{order.id}",
                        created_at=order_dt,
                    ))

                order.total_amount = order_total
                db.flush()

        # ---- Extra CustomerEvents (views, searches, cart adds) ---------------
        print("📱 Creating browse events...")
        event_types_no_purchase = [CustomerEventType.VIEW, CustomerEventType.SEARCH, CustomerEventType.CART_ADD]
        for _ in range(300):
            ev_dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
                days=rng.randint(0, 14), hours=rng.randint(0, 23)
            )
            db.add(CustomerEvent(
                customer_id=rng.choice(customers).id,
                product_id=rng.choice(products).id,
                dark_store_id=rng.choice(stores).id,
                event_type=rng.choice(event_types_no_purchase),
                session_id=f"BROWSE-{rng.randint(1000,9999)}",
                search_query="milk" if rng.random() < 0.3 else None,
                created_at=ev_dt,
            ))

        # High-view/low-purchase product: P0010 Almonds
        for _ in range(80):
            ev_dt = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=rng.randint(0, 7))
            db.add(CustomerEvent(
                customer_id=rng.choice(customers).id,
                product_id=products[9].id,  # Almonds
                dark_store_id=stores[0].id,
                event_type=CustomerEventType.VIEW,
                session_id=f"VW-{rng.randint(10000,99999)}",
                created_at=ev_dt,
            ))
        db.flush()

        # ---- Reviews --------------------------------------------------------
        print("⭐ Creating reviews...")
        for i in range(40):
            db.add(Review(
                customer_id=rng.choice(customers).id,
                product_id=rng.choice(products).id,
                dark_store_id=rng.choice(stores).id,
                rating=rng.randint(3, 5),
                text=rng.choice([
                    "Great quality!", "Fast delivery", "Fresh product",
                    "Good value for money", "Will buy again",
                    "Packaging was damaged", "Slightly overpriced",
                ]),
                sentiment_score=round(rng.uniform(0.3, 1.0), 3),
            ))
        db.flush()

        # ---- Weather (last 7 days + today) ----------------------------------
        print("🌤  Creating weather records...")
        conditions = list(WeatherCondition)
        for store in stores:
            for day_offset in range(7, -1, -1):
                d = today - datetime.timedelta(days=day_offset)
                db.add(Weather(
                    dark_store_id=store.id,
                    date=d,
                    condition=rng.choice(conditions),
                    temperature_c=round(rng.uniform(18, 38), 1),
                    humidity_pct=round(rng.uniform(40, 90), 1),
                    rainfall_mm=round(rng.uniform(0, 15), 1) if rng.random() < 0.3 else 0,
                ))
        db.flush()

        # ---- Festivals ------------------------------------------------------
        print("🎉 Creating festival records...")
        festivals = [
            ("Delhi", "Diwali", today + datetime.timedelta(days=5), 1.8),
            ("Bangalore", "Dasara", today + datetime.timedelta(days=12), 1.5),
            ("Mumbai", "Ganesh Chaturthi", today + datetime.timedelta(days=3), 1.6),
            ("Hyderabad", "Bonalu", today + datetime.timedelta(days=20), 1.3),
            ("Delhi", "Republic Day", today + datetime.timedelta(days=60), 0.7),
        ]
        for city, name, date, multiplier in festivals:
            db.add(Festival(city=city, name=name, date=date, demand_multiplier=multiplier,
                            description=f"Annual {name} festival"))
        db.flush()

        # ---- Trends (last 14 days) ------------------------------------------
        print("📈 Creating trend records...")
        trend_config = {
            0: (DemandTrend.DECLINING, 30),   # P0001 Milk — declining
            1: (DemandTrend.STABLE, 50),      # P0002 Bread
            2: (DemandTrend.STABLE, 55),      # P0003 Rice
            3: (DemandTrend.INCREASING, 78),  # P0004 Chips — trending UP
            4: (DemandTrend.STABLE, 60),
            5: (DemandTrend.INCREASING, 82),  # P0006 Maggi — trending
            6: (DemandTrend.DECLINING, 25),   # P0007 Spinach — declining
            7: (DemandTrend.STABLE, 45),
            8: (DemandTrend.INCREASING, 70),
            9: (DemandTrend.INCREASING, 88),  # Almonds — trending UP (high views)
            10: (DemandTrend.STABLE, 50),
            11: (DemandTrend.DECLINING, 35),
        }
        seen = set()
        for prod_idx, (trend_dir, base_score) in trend_config.items():
            for day_offset in range(14, -1, -1):
                d = today - datetime.timedelta(days=day_offset)
                key = (products[prod_idx].id, d)
                if key in seen:
                    continue
                seen.add(key)
                jitter = rng.uniform(-5, 5)
                db.add(Trend(
                    product_id=products[prod_idx].id,
                    date=d,
                    trend_score=round(max(0, min(100, base_score + jitter)), 2),
                    demand_trend=trend_dir,
                    sales_velocity=round(rng.uniform(2, 20), 2),
                    search_volume=rng.randint(10, 500),
                ))
        db.flush()

        # ---- Competitor Prices ----------------------------------------------
        print("💲 Creating competitor prices...")
        competitors = ["Blinkit", "Zepto", "BigBasket", "Swiggy Instamart"]
        for prod in products[:8]:
            for store in stores[:3]:
                comp_price = float(prod.mrp) * rng.uniform(0.85, 1.10)
                db.add(CompetitorPrice(
                    product_id=prod.id,
                    dark_store_id=store.id,
                    competitor_name=rng.choice(competitors),
                    competitor_price=round(comp_price, 2),
                    our_price=float(prod.mrp),
                ))
        db.flush()

        db.commit()
        print("\n✅ Seed complete!")
        print(f"   Retailers: 2, Stores: 5, Products: {len(products)}")
        print(f"   Customers: 50, Inventory records: {len(inventory_records)}")
        print(f"   Demo credentials: admin@freshmart.in / Demo@1234")
        print(f"   Demo credentials: admin@quickbasket.in / Demo@1234")
        print("\n🎯 Interesting scenarios seeded:")
        print("   🔴 P0059 (Full Cream Milk 1L) — DEL-DS1: CRITICAL expiry (0 days)")
        print("   🔴 P0007 (Spinach) — DEL-DS1: CRITICAL expiry + understock")
        print("   🟠 P0005 (Coke) — DEL-DS1: STOCKOUT")
        print("   🟠 P0003 (Basmati Rice) — DEL-DS1: OVERSTOCK (500 units, max 100)")
        print("   🟠 P0006 (Maggi) — DEL-DS1: OVERSTOCK + TRENDING UP")
        print("   🟡 P0010 (Almonds) — DEL-DS1: High views (80), low purchases")
        print("   📈 P0004 (Chips) — trending UP (score 78/100)")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_tables()
    seed()
