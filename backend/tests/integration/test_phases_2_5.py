"""
Integration tests for inventory, promotion, analytics, and chat endpoints.
Uses the in-memory SQLite test DB (conftest.py) with pre-seeded demo data.
"""

import datetime
import pytest
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.retailer import Retailer, User
from app.models.store import DarkStore
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.context import Trend
from app.utils.enums import (
    CustomerSegment, DemandTrend, StoreStatus, UserRole,
    PromotionObjective,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def seeded_db(db):
    """Set up minimal data needed for integration tests."""
    retailer = Retailer(name="TestMart", email="tm@test.com")
    db.add(retailer)
    db.flush()

    user = User(
        email="admin@testmart.com",
        password_hash=hash_password("TestPass1!"),
        role=UserRole.RETAILER_ADMIN,
        retailer_id=retailer.id,
        is_active=True,
    )
    db.add(user)
    db.flush()

    store = DarkStore(retailer_id=retailer.id, name="Test Store 1",
                      code="TST-DS1", city="Delhi", status=StoreStatus.ACTIVE)
    db.add(store)
    db.flush()

    # Products
    p_milk = Product(sku="TST-001", name="Test Milk", category="Dairy",
                     mrp=30, cost_price=20, shelf_life_days=2)
    p_rice = Product(sku="TST-002", name="Test Rice", category="Grains",
                     mrp=450, cost_price=310, shelf_life_days=365)
    p_expiry = Product(sku="TST-003", name="Test Expiry Item", category="Dairy",
                       mrp=62, cost_price=44, shelf_life_days=1)
    db.add_all([p_milk, p_rice, p_expiry])
    db.flush()

    # Inventory — interesting scenarios
    today = datetime.date.today()

    inv_understock = Inventory(
        dark_store_id=store.id, product_id=p_milk.id,
        quantity_available=5, quantity_reserved=0, reorder_point=20, max_stock=100,
        batch_number="BATCH-A",
    )
    inv_overstock = Inventory(
        dark_store_id=store.id, product_id=p_rice.id,
        quantity_available=500, quantity_reserved=0, reorder_point=20, max_stock=100,
        batch_number="BATCH-B",
    )
    inv_expiry = Inventory(
        dark_store_id=store.id, product_id=p_expiry.id,
        quantity_available=50, quantity_reserved=0, reorder_point=5, max_stock=30,
        batch_number="BATCH-C", expiry_date=today,  # expires TODAY → CRITICAL
    )
    db.add_all([inv_understock, inv_overstock, inv_expiry])
    db.flush()

    # Trend for expiry product — declining
    db.add(Trend(
        product_id=p_expiry.id, date=today,
        trend_score=25.0, demand_trend=DemandTrend.DECLINING,
    ))
    db.flush()

    return {
        "retailer": retailer, "user": user, "store": store,
        "p_milk": p_milk, "p_rice": p_rice, "p_expiry": p_expiry,
        "inv_understock": inv_understock, "inv_overstock": inv_overstock,
        "inv_expiry": inv_expiry,
    }


@pytest.fixture
def auth_headers(client, seeded_db):
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@testmart.com",
        "password": "TestPass1!",
    })
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


# ---------------------------------------------------------------------------
# Inventory endpoints
# ---------------------------------------------------------------------------

class TestInventoryEndpoints:

    def test_list_inventory_returns_200(self, client, seeded_db, auth_headers):
        resp = client.get("/api/v1/inventory", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) >= 3

    def test_inventory_has_effective_stock(self, client, seeded_db, auth_headers):
        resp = client.get("/api/v1/inventory", headers=auth_headers)
        for item in resp.json():
            assert "effective_stock" in item
            assert item["effective_stock"] >= 0

    def test_inventory_enriched_with_product_fields(self, client, seeded_db, auth_headers):
        resp = client.get("/api/v1/inventory", headers=auth_headers)
        item = resp.json()[0]
        assert "product_sku" in item
        assert "product_name" in item
        assert "product_mrp" in item

    def test_alerts_returns_200_with_critical(self, client, seeded_db, auth_headers):
        resp = client.get("/api/v1/inventory/alerts", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "total_alerts" in body
        assert "critical_count" in body
        assert body["total_alerts"] > 0
        # We seeded a CRITICAL expiry
        assert body["critical_count"] >= 1

    def test_alerts_sorted_critical_first(self, client, seeded_db, auth_headers):
        resp = client.get("/api/v1/inventory/alerts", headers=auth_headers)
        alerts = resp.json()["alerts"]
        urgency_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        for i in range(len(alerts) - 1):
            assert urgency_order.get(alerts[i]["urgency"], 99) <= urgency_order.get(alerts[i+1]["urgency"], 99)

    def test_alerts_contain_required_fields(self, client, seeded_db, auth_headers):
        resp = client.get("/api/v1/inventory/alerts", headers=auth_headers)
        alert = resp.json()["alerts"][0]
        for field in ("store_id", "store_code", "product_id", "product_sku",
                      "product_name", "alert_type", "urgency", "message"):
            assert field in alert, f"Missing field: {field}"

    def test_store_inventory_endpoint(self, client, seeded_db, auth_headers):
        store_id = seeded_db["store"].id
        resp = client.get(f"/api/v1/stores/{store_id}/inventory", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 3

    def test_store_inventory_wrong_store_404(self, client, seeded_db, auth_headers):
        resp = client.get("/api/v1/stores/99999/inventory", headers=auth_headers)
        assert resp.status_code == 404

    def test_patch_inventory_updates_quantity(self, client, seeded_db, auth_headers):
        inv_id = seeded_db["inv_understock"].id
        resp = client.patch(
            f"/api/v1/inventory/{inv_id}",
            json={"quantity_available": 50},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["quantity_available"] == 50

    def test_inventory_requires_auth(self, client, seeded_db):
        resp = client.get("/api/v1/inventory")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Inventory calculations (unit-level via service)
# ---------------------------------------------------------------------------

class TestInventoryCalculations:

    def test_effective_stock_formula(self, db, seeded_db):
        from app.services.inventory import calc_effective_stock
        assert calc_effective_stock(100, 20) == 80
        assert calc_effective_stock(10, 20) == 0   # never negative

    def test_expiry_classification_critical(self, db):
        from app.services.inventory import calc_days_until_expiry, classify_expiry_urgency
        from app.utils.enums import UrgencyLevel
        expiry = datetime.date.today()
        days = calc_days_until_expiry(expiry)
        assert days == 0
        assert classify_expiry_urgency(days) == UrgencyLevel.CRITICAL

    def test_expiry_classification_warning(self, db):
        from app.services.inventory import classify_expiry_urgency
        from app.utils.enums import UrgencyLevel
        assert classify_expiry_urgency(5) == UrgencyLevel.MEDIUM
        assert classify_expiry_urgency(2) == UrgencyLevel.HIGH
        assert classify_expiry_urgency(1) == UrgencyLevel.HIGH
        assert classify_expiry_urgency(10) == UrgencyLevel.LOW
        assert classify_expiry_urgency(None) == UrgencyLevel.LOW

    def test_alerts_detect_understock(self, db, seeded_db):
        from app.services.inventory import classify_stock_alerts
        from app.utils.enums import InventoryAlertType
        inv = seeded_db["inv_understock"]
        db.refresh(inv)
        inv.product  # load relationship
        alerts = classify_stock_alerts(inv)
        types = [a["alert_type"] for a in alerts]
        assert InventoryAlertType.UNDERSTOCK in types

    def test_alerts_detect_overstock(self, db, seeded_db):
        from app.services.inventory import classify_stock_alerts
        from app.utils.enums import InventoryAlertType
        inv = seeded_db["inv_overstock"]
        db.refresh(inv)
        inv.product
        alerts = classify_stock_alerts(inv)
        types = [a["alert_type"] for a in alerts]
        assert InventoryAlertType.OVERSTOCK in types

    def test_alerts_detect_expiry_critical(self, db, seeded_db):
        from app.services.inventory import classify_stock_alerts
        from app.utils.enums import InventoryAlertType, UrgencyLevel
        inv = seeded_db["inv_expiry"]
        db.refresh(inv)
        inv.product
        alerts = classify_stock_alerts(inv)
        expiry_alerts = [a for a in alerts if a["alert_type"] == InventoryAlertType.EXPIRY]
        assert len(expiry_alerts) >= 1
        assert expiry_alerts[0]["urgency"] == UrgencyLevel.CRITICAL


# ---------------------------------------------------------------------------
# Promotion engine
# ---------------------------------------------------------------------------

class TestPromotionEngine:

    def test_recommend_returns_locked_contract(self, client, seeded_db, auth_headers):
        resp = client.post(
            "/api/v1/promotions/recommend",
            json={
                "product_id": seeded_db["p_expiry"].id,
                "dark_store_id": seeded_db["store"].id,
                "objective": "BALANCED",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        # Contract fields
        for field in ("product_id", "dark_store_id", "recommended_action",
                      "discount_pct", "reasons", "risk_flag", "options", "inventory_snapshot"):
            assert field in body, f"Missing contract field: {field}"

    def test_recommend_has_options(self, client, seeded_db, auth_headers):
        resp = client.post(
            "/api/v1/promotions/recommend",
            json={"product_id": seeded_db["p_rice"].id, "dark_store_id": seeded_db["store"].id},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        opts = resp.json()["options"]
        assert len(opts) >= 2
        for o in opts:
            for f in ("discount_pct", "expected_profit", "inventory_reduction_pct",
                      "stockout_risk_pct", "score"):
                assert f in o

    def test_recommend_expiry_product_flags_risk(self, client, seeded_db, auth_headers):
        resp = client.post(
            "/api/v1/promotions/recommend",
            json={"product_id": seeded_db["p_expiry"].id, "dark_store_id": seeded_db["store"].id,
                  "objective": "REDUCE_EXPIRY_WASTE"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        # Must have expiry-related reason
        reasons_text = " ".join(body["reasons"]).lower()
        assert "expiry" in reasons_text

    def test_recommend_invalid_product_returns_404(self, client, seeded_db, auth_headers):
        resp = client.post(
            "/api/v1/promotions/recommend",
            json={"product_id": 99999, "dark_store_id": seeded_db["store"].id},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_simulate_returns_result(self, client, seeded_db, auth_headers):
        resp = client.post(
            "/api/v1/promotions/simulate",
            json={
                "product_id": seeded_db["p_rice"].id,
                "dark_store_id": seeded_db["store"].id,
                "discount_pct": 20,
                "duration_days": 7,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        result = resp.json()["result"]
        for field in ("discount_pct", "expected_sales_units", "expected_revenue",
                      "expected_profit", "inventory_reduction_pct", "stockout_risk_pct"):
            assert field in result

    def test_simulate_negative_profit_shown_not_hidden(self, db, seeded_db):
        """Engine SHOWS negative-profit options for clearance objectives."""
        from app.services.promotion import PromotionEngine
        result = PromotionEngine.recommend(
            db,
            product_id=seeded_db["p_expiry"].id,
            store_id=seeded_db["store"].id,
            objective=PromotionObjective.REDUCE_EXPIRY_WASTE,
            max_discount_pct=80,
        )
        # Should have at least one option (even if profit is negative for clearance)
        assert len(result["options"]) >= 1

    def test_compare_endpoint(self, client, seeded_db, auth_headers):
        resp = client.post(
            "/api/v1/promotions/compare",
            json={
                "product_id": seeded_db["p_rice"].id,
                "dark_store_id": seeded_db["store"].id,
                "discount_pcts": [10, 20, 30],
                "duration_days": 7,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()["results"]) == 3

    def test_history_returns_list(self, client, seeded_db, auth_headers):
        # First generate a recommendation to populate history
        client.post(
            "/api/v1/promotions/recommend",
            json={"product_id": seeded_db["p_rice"].id, "dark_store_id": seeded_db["store"].id},
            headers=auth_headers,
        )
        resp = client.get("/api/v1/promotions/history", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


# ---------------------------------------------------------------------------
# Analytics endpoints
# ---------------------------------------------------------------------------

class TestAnalyticsEndpoints:

    def test_sales_returns_200(self, client, seeded_db, auth_headers):
        resp = client.get("/api/v1/analytics/sales?days=30", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert "data_points" in body
        assert "period_days" in body

    def test_trends_returns_200(self, client, seeded_db, auth_headers):
        resp = client.get("/api/v1/analytics/trends", headers=auth_headers)
        assert resp.status_code == 200
        assert "trending_products" in resp.json()

    def test_customers_returns_funnel(self, client, seeded_db, auth_headers):
        resp = client.get("/api/v1/analytics/customers", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        for field in ("total_views", "total_purchases", "view_to_purchase_rate"):
            assert field in body

    def test_stores_comparison(self, client, seeded_db, auth_headers):
        resp = client.get("/api/v1/analytics/stores", headers=auth_headers)
        assert resp.status_code == 200
        assert "stores" in resp.json()

    def test_demand_forecast(self, client, seeded_db, auth_headers):
        resp = client.get(
            f"/api/v1/analytics/demand?product_id={seeded_db['p_rice'].id}&store_id={seeded_db['store'].id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "forecast" in body
        assert len(body["forecast"]) == 7  # default

    def test_analytics_requires_auth(self, client, seeded_db):
        resp = client.get("/api/v1/analytics/sales")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------------------------

class TestChatEndpoint:

    def test_chat_demo_mode_returns_200(self, client, seeded_db, auth_headers):
        resp = client.post(
            "/api/v1/chat",
            json={"messages": [{"role": "user", "content": "Which products are overstocked?"}]},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "response" in body
        assert "demo_mode" in body
        assert body["demo_mode"] is True

    def test_chat_expiry_intent(self, client, seeded_db, auth_headers):
        resp = client.post(
            "/api/v1/chat",
            json={"messages": [{"role": "user", "content": "Which products are expiring soon?"}]},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["response"]  # non-empty response

    def test_chat_requires_auth(self, client, seeded_db):
        resp = client.post(
            "/api/v1/chat",
            json={"messages": [{"role": "user", "content": "hello"}]},
        )
        assert resp.status_code == 401

    def test_chat_empty_message_rejected(self, client, seeded_db, auth_headers):
        resp = client.post(
            "/api/v1/chat",
            json={"messages": [{"role": "user", "content": ""}]},
            headers=auth_headers,
        )
        assert resp.status_code == 422
