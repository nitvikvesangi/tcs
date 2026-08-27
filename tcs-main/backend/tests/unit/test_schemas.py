"""
Unit tests for Pydantic v2 schemas.

Pure Python — no database, no HTTP.  Tests validate:
  - Required fields and defaults.
  - Validation errors on missing / bad data.
  - The exact PromotionRecommendationResponse JSON contract.
"""

import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, UserRegisterRequest
from app.schemas.promotion import (
    InventorySnapshot,
    PromotionOption,
    PromotionRecommendationResponse,
)
from app.schemas.alerts import InventoryAlert, AlertsResponse
from app.schemas.simulation import SimulationResult
from app.utils.enums import InventoryAlertType, UrgencyLevel


# ---------------------------------------------------------------------------
# Auth schemas
# ---------------------------------------------------------------------------

class TestUserRegisterRequest:
    def test_valid_registration(self):
        data = UserRegisterRequest(
            email="admin@freshmart.in",
            password="Secr3t!Pass",
            full_name="Priya Sharma",
            retailer_name="FreshMart",
        )
        assert data.email == "admin@freshmart.in"
        assert data.full_name == "Priya Sharma"

    def test_missing_email_raises(self):
        with pytest.raises(ValidationError) as exc_info:
            UserRegisterRequest(password="ValidPass1!")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("email",) for e in errors)

    def test_short_password_raises(self):
        with pytest.raises(ValidationError):
            UserRegisterRequest(email="a@b.com", password="short")

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            UserRegisterRequest(email="not-an-email", password="ValidPass1!")

    def test_optional_fields_default_to_none(self):
        data = UserRegisterRequest(email="x@y.com", password="ValidPass1!")
        assert data.full_name is None
        assert data.retailer_name is None


class TestLoginRequest:
    def test_valid_login(self):
        data = LoginRequest(email="user@test.com", password="pass")
        assert data.email == "user@test.com"

    def test_empty_password_raises(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="user@test.com", password="")


# ---------------------------------------------------------------------------
# PromotionOption
# ---------------------------------------------------------------------------

class TestPromotionOption:
    def test_valid_option(self):
        opt = PromotionOption(
            discount_pct=25,
            expected_profit=47.6,
            inventory_reduction_pct=12.4,
            stockout_risk_pct=15.6,
            score=47.63,
        )
        assert opt.discount_pct == 25
        assert opt.expected_profit == 47.6

    def test_negative_expected_profit_allowed(self):
        """Options with negative profit are valid — retailer makes the final call."""
        opt = PromotionOption(
            discount_pct=45,
            expected_profit=-32.5,
            inventory_reduction_pct=14.4,
            stockout_risk_pct=16.6,
            score=-32.52,
        )
        assert opt.expected_profit == -32.5

    def test_discount_pct_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            PromotionOption(
                discount_pct=110,  # > 100
                expected_profit=10,
                inventory_reduction_pct=5,
                stockout_risk_pct=5,
                score=10,
            )


# ---------------------------------------------------------------------------
# InventorySnapshot
# ---------------------------------------------------------------------------

class TestInventorySnapshot:
    def test_valid_snapshot(self):
        snap = InventorySnapshot(
            stockout_urgency="High",
            overstock_urgency="Critical",
            expiry_urgency="Critical",
            inventory_alert_score=100,
        )
        assert snap.inventory_alert_score == 100

    def test_alert_score_out_of_range_raises(self):
        with pytest.raises(ValidationError):
            InventorySnapshot(
                stockout_urgency="High",
                overstock_urgency="Low",
                expiry_urgency="Low",
                inventory_alert_score=150,  # > 100
            )


# ---------------------------------------------------------------------------
# PromotionRecommendationResponse — the exact contract from project spec
# ---------------------------------------------------------------------------

SPEC_PAYLOAD = {
    "product_id": "P0059",
    "dark_store_id": "BEN-DS4",
    "recommended_action": "CLEARANCE",
    "discount_pct": 25,
    "reasons": ["expiry_urgency=Critical (0 days left of 1-day shelf life)"],
    "risk_flag": "EXPIRY_CRITICAL",
    "options": [
        {
            "discount_pct": 25,
            "expected_profit": 47.6,
            "inventory_reduction_pct": 12.4,
            "stockout_risk_pct": 15.6,
            "score": 47.63,
        },
        {
            "discount_pct": 35,
            "expected_profit": 10.0,
            "inventory_reduction_pct": 13.6,
            "stockout_risk_pct": 16.1,
            "score": 10.04,
        },
        {
            "discount_pct": 45,
            "expected_profit": -32.5,
            "inventory_reduction_pct": 14.4,
            "stockout_risk_pct": 16.6,
            "score": -32.52,
        },
    ],
    "inventory_snapshot": {
        "stockout_urgency": "High",
        "overstock_urgency": "Critical",
        "expiry_urgency": "Critical",
        "inventory_alert_score": 100,
    },
}


class TestPromotionRecommendationResponse:
    def test_spec_payload_validates(self):
        """The exact JSON from the project specification must validate."""
        rec = PromotionRecommendationResponse(**SPEC_PAYLOAD)
        assert rec.product_id == "P0059"
        assert rec.dark_store_id == "BEN-DS4"
        assert rec.recommended_action == "CLEARANCE"
        assert rec.discount_pct == 25
        assert rec.risk_flag == "EXPIRY_CRITICAL"

    def test_spec_payload_has_three_options(self):
        rec = PromotionRecommendationResponse(**SPEC_PAYLOAD)
        assert len(rec.options) == 3

    def test_spec_payload_option_values(self):
        rec = PromotionRecommendationResponse(**SPEC_PAYLOAD)
        opts = rec.options
        assert opts[0].discount_pct == 25
        assert opts[0].expected_profit == 47.6
        assert opts[1].expected_profit == 10.0
        assert opts[2].expected_profit == -32.5

    def test_spec_payload_inventory_snapshot(self):
        rec = PromotionRecommendationResponse(**SPEC_PAYLOAD)
        snap = rec.inventory_snapshot
        assert snap.stockout_urgency == "High"
        assert snap.overstock_urgency == "Critical"
        assert snap.expiry_urgency == "Critical"
        assert snap.inventory_alert_score == 100

    def test_spec_payload_reasons_preserved(self):
        rec = PromotionRecommendationResponse(**SPEC_PAYLOAD)
        assert "expiry_urgency=Critical (0 days left of 1-day shelf life)" in rec.reasons

    def test_roundtrip_json(self):
        """Serialise → parse → compare to ensure no data is lost."""
        rec = PromotionRecommendationResponse(**SPEC_PAYLOAD)
        as_json = rec.model_dump()
        rec2 = PromotionRecommendationResponse(**as_json)
        assert rec2.product_id == rec.product_id
        assert len(rec2.options) == len(rec.options)

    def test_missing_required_field_raises(self):
        bad = {k: v for k, v in SPEC_PAYLOAD.items() if k != "product_id"}
        with pytest.raises(ValidationError):
            PromotionRecommendationResponse(**bad)


# ---------------------------------------------------------------------------
# AlertsResponse
# ---------------------------------------------------------------------------

class TestAlertsSchema:
    def test_inventory_alert_creation(self):
        alert = InventoryAlert(
            store_id=1,
            store_code="DEL-DS1",
            product_id=59,
            product_sku="P0059",
            product_name="Milk 500ml",
            alert_type=InventoryAlertType.EXPIRY,
            urgency=UrgencyLevel.CRITICAL,
            message="Product expires in 0 days",
            details={"days_until_expiry": 0},
        )
        assert alert.alert_type == InventoryAlertType.EXPIRY
        assert alert.urgency == UrgencyLevel.CRITICAL


# ---------------------------------------------------------------------------
# SimulationResult
# ---------------------------------------------------------------------------

class TestSimulationResult:
    def test_valid_simulation_result(self):
        res = SimulationResult(
            discount_pct=20,
            expected_sales_units=150.0,
            expected_revenue=4800.0,
            expected_profit=960.0,
            inventory_reduction_pct=30.0,
            stockout_risk_pct=10.0,
            expiry_waste_reduction_pct=75.0,
            profit_impact_pct=5.0,
        )
        assert res.discount_pct == 20
        assert res.expected_profit == 960.0
