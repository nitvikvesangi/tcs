"""
Unit tests for all 16 ORM models.

Uses the `db` fixture from conftest.py (SQLite, rolled back per test).
Tests verify: column defaults, FKs, relationships, unique constraints,
and the Inventory.effective_stock computed property.
"""

import datetime

import pytest

from app.models import (
    CompetitorPrice,
    Customer,
    CustomerEvent,
    DarkStore,
    Festival,
    Inventory,
    Order,
    OrderItem,
    Product,
    Promotion,
    PromotionPerformance,
    Retailer,
    Review,
    Trend,
    User,
    Weather,
)
from app.utils.enums import (
    CustomerEventType,
    CustomerSegment,
    DemandTrend,
    OrderStatus,
    PromotionObjective,
    PromotionStatus,
    PromotionType,
    RiskFlag,
    StoreStatus,
    UserRole,
    WeatherCondition,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_retailer(db, name="FreshMart", email="freshmart@test.com"):
    r = Retailer(name=name, email=email)
    db.add(r)
    db.flush()
    return r


def make_store(db, retailer, code="DEL-DS1", city="Delhi"):
    s = DarkStore(retailer_id=retailer.id, name="Store 1", code=code, city=city, status=StoreStatus.ACTIVE)
    db.add(s)
    db.flush()
    return s


def make_product(db, sku="P0001", shelf_life=0):
    p = Product(sku=sku, name="Milk 500ml", category="Dairy", mrp=40.0, cost_price=28.0, shelf_life_days=shelf_life)
    db.add(p)
    db.flush()
    return p


def make_customer(db, retailer):
    c = Customer(retailer_id=retailer.id, segment=CustomerSegment.NEW_CUSTOMER)
    db.add(c)
    db.flush()
    return c


# ---------------------------------------------------------------------------
# Retailer
# ---------------------------------------------------------------------------

class TestRetailer:
    def test_create_retailer(self, db):
        r = make_retailer(db)
        assert r.id is not None
        assert r.name == "FreshMart"

    def test_retailer_email_unique(self, db):
        make_retailer(db, email="dup@test.com")
        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            make_retailer(db, name="Dup2", email="dup@test.com")

    def test_retailer_defaults(self, db):
        r = Retailer(name="Quick", email="quick@test.com")
        db.add(r)
        db.flush()
        assert r.phone is None
        assert r.city is None


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class TestUser:
    def test_create_user(self, db):
        r = make_retailer(db)
        u = User(
            email="admin@test.com",
            password_hash="hashed",
            role=UserRole.RETAILER_ADMIN,
            retailer_id=r.id,
        )
        db.add(u)
        db.flush()
        assert u.id is not None
        assert u.is_active is True

    def test_user_email_unique(self, db):
        from sqlalchemy.exc import IntegrityError
        r = make_retailer(db)
        u1 = User(email="same@test.com", password_hash="h", role=UserRole.ANALYST, retailer_id=r.id)
        db.add(u1)
        db.flush()
        u2 = User(email="same@test.com", password_hash="h", role=UserRole.ANALYST)
        db.add(u2)
        with pytest.raises(IntegrityError):
            db.flush()

    def test_user_default_role(self, db):
        u = User(email="newuser@test.com", password_hash="h")
        db.add(u)
        db.flush()
        assert u.role == UserRole.RETAILER_ADMIN


# ---------------------------------------------------------------------------
# DarkStore
# ---------------------------------------------------------------------------

class TestDarkStore:
    def test_create_store(self, db):
        r = make_retailer(db)
        s = make_store(db, r)
        assert s.id is not None
        assert s.code == "DEL-DS1"
        assert s.status == StoreStatus.ACTIVE

    def test_store_code_unique(self, db):
        from sqlalchemy.exc import IntegrityError
        r = make_retailer(db)
        make_store(db, r, code="UNIQUE-001")
        s2 = DarkStore(retailer_id=r.id, name="S2", code="UNIQUE-001", city="Mumbai", status=StoreStatus.ACTIVE)
        db.add(s2)
        with pytest.raises(IntegrityError):
            db.flush()

    def test_retailer_relationship(self, db):
        r = make_retailer(db)
        s = make_store(db, r)
        db.refresh(s)
        assert s.retailer_id == r.id


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------

class TestProduct:
    def test_create_product(self, db):
        p = make_product(db)
        assert p.id is not None
        assert p.sku == "P0001"
        assert p.is_active is True

    def test_sku_unique(self, db):
        from sqlalchemy.exc import IntegrityError
        make_product(db, sku="DUP001")
        p2 = Product(sku="DUP001", name="Dup", category="Test", mrp=10, cost_price=5, shelf_life_days=0)
        db.add(p2)
        with pytest.raises(IntegrityError):
            db.flush()

    def test_perishable_product(self, db):
        p = make_product(db, sku="MILK001", shelf_life=3)
        assert p.shelf_life_days == 3


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

class TestInventory:
    def test_create_inventory(self, db):
        r = make_retailer(db)
        s = make_store(db, r)
        p = make_product(db)
        inv = Inventory(
            dark_store_id=s.id,
            product_id=p.id,
            quantity_available=100,
            quantity_reserved=10,
            reorder_point=20,
        )
        db.add(inv)
        db.flush()
        assert inv.id is not None
        assert inv.quantity_available == 100

    def test_effective_stock(self, db):
        r = make_retailer(db)
        s = make_store(db, r)
        p = make_product(db)
        inv = Inventory(
            dark_store_id=s.id, product_id=p.id,
            quantity_available=50, quantity_reserved=15, reorder_point=0,
        )
        db.add(inv)
        db.flush()
        assert inv.effective_stock == 35

    def test_effective_stock_never_negative(self, db):
        r = make_retailer(db)
        s = make_store(db, r)
        p = make_product(db)
        inv = Inventory(
            dark_store_id=s.id, product_id=p.id,
            quantity_available=5, quantity_reserved=20, reorder_point=0,
        )
        db.add(inv)
        db.flush()
        assert inv.effective_stock == 0

    def test_expiry_date_stored(self, db):
        r = make_retailer(db)
        s = make_store(db, r)
        p = make_product(db, sku="EXP001", shelf_life=3)
        expiry = datetime.date.today() + datetime.timedelta(days=3)
        inv = Inventory(
            dark_store_id=s.id, product_id=p.id,
            quantity_available=30, quantity_reserved=0,
            reorder_point=5, expiry_date=expiry,
        )
        db.add(inv)
        db.flush()
        assert inv.expiry_date == expiry

    def test_multiple_batches_same_product_allowed(self, db):
        """Multiple inventory rows per (store, product) are valid — batch tracking."""
        r = make_retailer(db)
        s = make_store(db, r)
        p = make_product(db)
        inv1 = Inventory(dark_store_id=s.id, product_id=p.id,
                         quantity_available=20, quantity_reserved=0, reorder_point=0,
                         batch_number="BATCH-A")
        inv2 = Inventory(dark_store_id=s.id, product_id=p.id,
                         quantity_available=30, quantity_reserved=0, reorder_point=0,
                         batch_number="BATCH-B")
        db.add_all([inv1, inv2])
        db.flush()
        assert inv1.id != inv2.id


# ---------------------------------------------------------------------------
# Customer + CustomerEvent
# ---------------------------------------------------------------------------

class TestCustomer:
    def test_create_customer(self, db):
        r = make_retailer(db)
        c = make_customer(db, r)
        assert c.id is not None
        assert c.segment == CustomerSegment.NEW_CUSTOMER

    def test_customer_event(self, db):
        r = make_retailer(db)
        s = make_store(db, r)
        p = make_product(db)
        c = make_customer(db, r)
        ev = CustomerEvent(
            customer_id=c.id, product_id=p.id, dark_store_id=s.id,
            event_type=CustomerEventType.VIEW,
        )
        db.add(ev)
        db.flush()
        assert ev.id is not None
        assert ev.event_type == CustomerEventType.VIEW


# ---------------------------------------------------------------------------
# Order + OrderItem
# ---------------------------------------------------------------------------

class TestOrder:
    def test_create_order_with_items(self, db):
        r = make_retailer(db)
        s = make_store(db, r)
        p = make_product(db)
        c = make_customer(db, r)
        order = Order(
            customer_id=c.id, dark_store_id=s.id,
            status=OrderStatus.PLACED, total_amount=80.0, discount_amount=0,
        )
        db.add(order)
        db.flush()
        item = OrderItem(
            order_id=order.id, product_id=p.id,
            quantity=2, unit_price=40.0, discount_pct=0, total_price=80.0,
        )
        db.add(item)
        db.flush()
        assert item.id is not None
        assert item.quantity == 2


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------

class TestReview:
    def test_create_review(self, db):
        r = make_retailer(db)
        s = make_store(db, r)
        p = make_product(db)
        c = make_customer(db, r)
        rev = Review(
            customer_id=c.id, product_id=p.id, dark_store_id=s.id,
            rating=5, text="Great milk!",
        )
        db.add(rev)
        db.flush()
        assert rev.id is not None
        assert rev.sentiment_score is None  # populated by Phase 3 ML


# ---------------------------------------------------------------------------
# Promotion + PromotionPerformance
# ---------------------------------------------------------------------------

class TestPromotion:
    def test_create_promotion(self, db):
        r = make_retailer(db)
        s = make_store(db, r)
        p = make_product(db)
        promo = Promotion(
            product_id=p.id, dark_store_id=s.id,
            promotion_type=PromotionType.CLEARANCE,
            objective=PromotionObjective.REDUCE_EXPIRY_WASTE,
            status=PromotionStatus.RECOMMENDED,
            discount_pct=25.0, risk_flag=RiskFlag.EXPIRY_CRITICAL,
        )
        db.add(promo)
        db.flush()
        assert promo.id is not None
        assert promo.status == PromotionStatus.RECOMMENDED

    def test_recommendation_data_json_stored(self, db):
        r = make_retailer(db)
        s = make_store(db, r)
        p = make_product(db)
        payload = {
            "product_id": p.sku,
            "options": [{"discount_pct": 25, "score": 47.6}],
        }
        promo = Promotion(
            product_id=p.id, dark_store_id=s.id,
            promotion_type=PromotionType.CLEARANCE,
            objective=PromotionObjective.BALANCED,
            status=PromotionStatus.RECOMMENDED,
            discount_pct=25, risk_flag=RiskFlag.NONE,
            recommendation_data=payload,
        )
        db.add(promo)
        db.flush()
        db.refresh(promo)
        assert promo.recommendation_data["options"][0]["discount_pct"] == 25

    def test_promotion_performance(self, db):
        r = make_retailer(db)
        s = make_store(db, r)
        p = make_product(db)
        promo = Promotion(
            product_id=p.id, dark_store_id=s.id,
            promotion_type=PromotionType.PERCENTAGE_DISCOUNT,
            objective=PromotionObjective.MAXIMIZE_PROFIT,
            status=PromotionStatus.APPROVED,
            discount_pct=10, risk_flag=RiskFlag.NONE,
        )
        db.add(promo)
        db.flush()
        perf = PromotionPerformance(
            promotion_id=promo.id, date=datetime.date.today(),
            units_sold=50, revenue=2000.0, profit=400.0, stockout_occurred=False,
        )
        db.add(perf)
        db.flush()
        assert perf.id is not None


# ---------------------------------------------------------------------------
# Context models
# ---------------------------------------------------------------------------

class TestContextModels:
    def test_weather(self, db):
        r = make_retailer(db)
        s = make_store(db, r)
        w = Weather(
            dark_store_id=s.id, date=datetime.date.today(),
            condition=WeatherCondition.RAINY, temperature_c=22.5,
        )
        db.add(w)
        db.flush()
        assert w.id is not None

    def test_weather_unique_per_store_date(self, db):
        from sqlalchemy.exc import IntegrityError
        r = make_retailer(db)
        s = make_store(db, r, code="WX-STORE")
        today = datetime.date.today()
        db.add(Weather(dark_store_id=s.id, date=today, condition=WeatherCondition.SUNNY))
        db.flush()
        db.add(Weather(dark_store_id=s.id, date=today, condition=WeatherCondition.RAINY))
        with pytest.raises(IntegrityError):
            db.flush()

    def test_festival(self, db):
        f = Festival(city="Delhi", name="Diwali", date=datetime.date(2026, 10, 20), demand_multiplier=1.8)
        db.add(f)
        db.flush()
        assert f.id is not None

    def test_trend(self, db):
        p = make_product(db, sku="TREND01")
        t = Trend(
            product_id=p.id, date=datetime.date.today(),
            trend_score=75.0, demand_trend=DemandTrend.INCREASING,
        )
        db.add(t)
        db.flush()
        assert t.id is not None

    def test_trend_unique_per_product_date(self, db):
        from sqlalchemy.exc import IntegrityError
        p = make_product(db, sku="TDUP01")
        today = datetime.date.today()
        db.add(Trend(product_id=p.id, date=today, trend_score=50, demand_trend=DemandTrend.STABLE))
        db.flush()
        db.add(Trend(product_id=p.id, date=today, trend_score=60, demand_trend=DemandTrend.INCREASING))
        with pytest.raises(IntegrityError):
            db.flush()

    def test_competitor_price(self, db):
        r = make_retailer(db)
        s = make_store(db, r, code="CP-STORE")
        p = make_product(db, sku="CP001")
        cp = CompetitorPrice(
            product_id=p.id, dark_store_id=s.id,
            competitor_name="Blinkit", competitor_price=38.0, our_price=40.0,
        )
        db.add(cp)
        db.flush()
        assert cp.id is not None
